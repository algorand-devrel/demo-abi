import os
from inspect import *
from typing import Callable
from Cryptodome.Hash import SHA512

from pyteal import *


return_prefix = Bytes("base16", "0x151f7c75")  # Literally hash('return')[:4]


@Subroutine(TealType.uint64)
def wrap_return_bytes(b: TealType.bytes) -> Expr:
    return Seq(Log(Concat(return_prefix, b)), Int(1))


@Subroutine(TealType.uint64)
def wrap_return_int(b: TealType.uint64) -> Expr:
    return Seq(Log(Concat(return_prefix, Itob(b))), Int(1))


@Subroutine(TealType.uint64)
def add(a: TealType.uint64, b: TealType.uint64) -> Expr:
    return a + b


@Subroutine(TealType.uint64)
def sub(a: TealType.uint64, b: TealType.uint64) -> Expr:
    return a - b


@Subroutine(TealType.uint64)
def mul(a: TealType.uint64, b: TealType.uint64) -> Expr:
    return a * b


@Subroutine(TealType.uint64)
def div(a: TealType.uint64, b: TealType.uint64) -> Expr:
    return a / b


@Subroutine(TealType.uint64)
def mod(a: TealType.uint64, b: TealType.uint64) -> Expr:
    return a % b


@Subroutine(TealType.bytes)
def qrem(a: TealType.uint64, b: TealType.uint64) -> Expr:
    return Concat(Itob(div(a, b)), Itob(mod(a, b)))


@Subroutine(TealType.bytes)
def reverse(a: TealType.bytes) -> Expr:
    idx = ScratchVar()
    buff = ScratchVar()

    init = idx.store(ExtractUint16(a, Int(0)) + Int(1))
    cond = idx.load() >= Int(2)
    iter = idx.store(idx.load() - Int(1))
    return Seq(
        buff.store(Bytes("")),
        For(init, cond, iter).Do(
            buff.store(Concat(buff.load(), Extract(a, idx.load(), Int(1))))
        ),
        prepend_length(buff.load()),
    )


@Subroutine(TealType.bytes)
def prepend_length(b: TealType.bytes) -> Expr:
    return Concat(Extract(Itob(Len(b)), Int(6), Int(2)), b)


def txntest(a: TealType.uint64, b: TealType.uint64):
    return And(
        Gtxn[Txn.group_index() - Int(1)].amount() == a,
        Gtxn[Txn.group_index() - Int(1)].fee() == b,
    )


@Subroutine(TealType.uint64)
def _optIn(a: TealType.uint64) -> Expr:
    return a


@Subroutine(TealType.uint64)
def _closeOut(a: TealType.uint64) -> Expr:
    return a


@Subroutine(TealType.uint64)
def manyargs(
    a: TealType.uint64,
    b: TealType.uint64,
    c: TealType.uint64,
    d: TealType.uint64,
    e: TealType.uint64,
    f: TealType.uint64,
    g: TealType.uint64,
    h: TealType.uint64,
    i: TealType.uint64,
    j: TealType.uint64,
    k: TealType.uint64,
    l: TealType.uint64,
    m: TealType.uint64,
    n: TealType.uint64,
    o: TealType.uint64,
    p: TealType.uint64,
    q: TealType.uint64,
    r: TealType.uint64,
    s: TealType.uint64,
    t: TealType.uint64,
):
    return a


@Subroutine(TealType.uint64)
def min_bal(idx: TealType.uint64):
    #return MinBalance(Txn.accounts[idx]) should be passed the actual index, currently py-sdk passes index without implicit + 1 from sender
    return MinBalance(Txn.accounts[idx+Int(1)])


def typestring(a):
    typedict = {
        TealType.uint64: "uint64",
        TealType.bytes: "string",
    }
    return typedict[a]


def selector(f: Callable) -> str:
    sig = signature(f)
    args = [typestring(p[1].annotation) for p in sig.parameters.items()]
    ret = typestring(f.__closure__[0].cell_contents.returnType)
    method = "{}({}){}".format(f.__name__, ",".join(args), ret)

    return hashy(method)


def hashy(method: str) -> Bytes:
    chksum = SHA512.new(truncate="256")
    chksum.update(method.encode())
    return Bytes(chksum.digest()[:4])


def approval():
    is_app_creator = Txn.sender() == Global.creator_address()

    add_sel = selector(add)
    sub_sel = selector(sub)
    mul_sel = selector(mul)
    div_sel = selector(div)

    reverse_sel = selector(reverse)
    many_sel = selector(manyargs)


    optin_sel = selector(_optIn)
    close_sel = selector(_closeOut)

    # Types Dont work with selector function
    qrem_sel = hashy("qrem(uint64,uin64)(uint64,uint64)")
    txn_sel = hashy("txntest(uint64,pay,uint64)uint64")
    min_sel = hashy("min_bal(account)uint64")

    router = Cond(
        [
            Txn.application_args[0] == add_sel,
            wrap_return_int(
                add(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))
            ),
        ],
        [
            Txn.application_args[0] == sub_sel,
            wrap_return_int(
                sub(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))
            ),
        ],
        [
            Txn.application_args[0] == mul_sel,
            wrap_return_int(
                mul(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))
            ),
        ],
        [
            Txn.application_args[0] == div_sel,
            wrap_return_int(
                div(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))
            ),
        ],
        [
            Txn.application_args[0] == qrem_sel,
            wrap_return_bytes(
                qrem(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))
            ),
        ],
        [
            Txn.application_args[0] == reverse_sel,
            wrap_return_bytes(reverse(Txn.application_args[1])),
        ],
        [
            Txn.application_args[0] == txn_sel,
            wrap_return_int(
                txntest(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))
            ),
        ],
        [
            Txn.application_args[0] == many_sel,
            wrap_return_int(
                manyargs(
                    Btoi(Txn.application_args[1]),
                    Btoi(Txn.application_args[2]),
                    Btoi(Txn.application_args[3]),
                    Btoi(Txn.application_args[4]),
                    Btoi(Txn.application_args[5]),
                    Btoi(Txn.application_args[6]),
                    Btoi(Txn.application_args[7]),
                    Btoi(Txn.application_args[8]),
                    Btoi(Txn.application_args[9]),
                    Btoi(Txn.application_args[10]),
                    Btoi(Txn.application_args[11]),
                    Btoi(Txn.application_args[12]),
                    Btoi(Txn.application_args[13]),
                    Btoi(Txn.application_args[14]),
                    ExtractUint64(Txn.application_args[15], Int(0)),
                    ExtractUint64(Txn.application_args[15], Int(8)),
                    ExtractUint64(Txn.application_args[15], Int(16)),
                    ExtractUint64(Txn.application_args[15], Int(24)),
                    ExtractUint64(Txn.application_args[15], Int(32)),
                    ExtractUint64(Txn.application_args[15], Int(40)),
                )
            ),
        ],
        [
            Txn.application_args[0] == min_sel,
            wrap_return_int(min_bal(Btoi(Txn.application_args[1]))),
        ],
        [
            Txn.application_args[0] == optin_sel,
            wrap_return_int(_optIn(Btoi(Txn.application_args[1]))),
        ],
        [
            Txn.application_args[0] == close_sel,
            wrap_return_int(_closeOut(Btoi(Txn.application_args[1]))),
        ],
    )

    @Subroutine(TealType.uint64)
    def route_or_allow() -> Expr:
        return If(Txn.application_args.length() > Int(0)).Then(router).Else(Int(0))

    return Cond(
        [Txn.application_id() == Int(0), Int(1)],
        [Txn.on_completion() == OnComplete.DeleteApplication, is_app_creator],
        [Txn.on_completion() == OnComplete.UpdateApplication, is_app_creator],
        [Txn.on_completion() == OnComplete.CloseOut, route_or_allow()],
        [Txn.on_completion() == OnComplete.OptIn, route_or_allow()],
        [Txn.on_completion() == OnComplete.NoOp, router],
    )


def clear():
    return Return(Int(1))


if __name__ == "__main__":

    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(
            compileTeal(
                approval(), mode=Mode.Application, version=5, assembleConstants=True
            )
        )

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(
            compileTeal(
                clear(), mode=Mode.Application, version=5, assembleConstants=True
            )
        )
