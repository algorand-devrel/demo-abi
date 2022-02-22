import os
from inspect import *
from typing import Callable, List
from Cryptodome.Hash import SHA512

from pyteal import *


# All return values are prefixed with this const and logged.
# Only the last log message with this prefix will be considered the return value
return_prefix = Bytes("base16", "0x151f7c75")  # Literally hash('return')[:4]


# Utility function to concat the return const and log the return value
@Subroutine(TealType.uint64)
def wrap_return(b) -> Expr:
    return Seq(Log(Concat(return_prefix, b)), Int(1))


@Subroutine(TealType.uint64)
def add(a, b) -> Expr:
    return a + b


@Subroutine(TealType.uint64)
def sub(a, b) -> Expr:
    return a - b


@Subroutine(TealType.uint64)
def mul(a, b) -> Expr:
    return a * b


@Subroutine(TealType.uint64)
def div(a, b) -> Expr:
    return a / b


@Subroutine(TealType.uint64)
def mod(a, b) -> Expr:
    return a % b


@Subroutine(TealType.bytes)
def qrem(a, b) -> Expr:
    return Concat(Itob(div(a, b)), Itob(mod(a, b)))


@Subroutine(TealType.bytes)
def reverse(a) -> Expr:
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
        # Prefix bytestring with its length, according to spec
        prepend_length(buff.load()),
    )


@Subroutine(TealType.bytes)
def concat_strings(b) -> Expr:
    idx = ScratchVar()
    buff = ScratchVar()
    pos = ScratchVar()

    init = idx.store(Int(0))
    cond = idx.load() < ExtractUint16(b, Int(0))
    iter = idx.store(idx.load() + Int(1))
    return Seq(
        buff.store(Bytes("")),
        pos.store(Int(0)),
        For(init, cond, iter).Do(
            Seq(
                pos.store(ExtractUint16(b, (idx.load() * Int(2)) + Int(2)) + Int(2)),
                buff.store(
                    Concat(
                        buff.load(),
                        Extract(b, pos.load() + Int(2), ExtractUint16(b, pos.load())),
                    )
                ),
            )
        ),
        prepend_length(buff.load()),
    )


@Subroutine(TealType.bytes)
def prepend_length(b) -> Expr:
    return Concat(Extract(Itob(Len(b)), Int(6), Int(2)), b)


def txntest(a, b):
    return And(
        Gtxn[Txn.group_index() - Int(1)].amount() == a,
        Gtxn[Txn.group_index() - Int(1)].fee() == b,
    )

@Subroutine(TealType.uint64)
def manyargs(a: Expr, b: Expr, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t):
    return a


@Subroutine(TealType.uint64)
def min_bal(idx):
    return MinBalance(Txn.accounts[idx])


def typestring(a):
    typedict = {
        TealType.uint64: "uint64",
        TealType.bytes: "string",
    }
    return typedict[a]


# Utility function to turn a subroutine callable into its selector
# It produces the method signature `name(type1,type2,...)returnType`
# which is passed to the `hashy` method to be turned into the method selector
def get_method_selector(f: Callable) -> str:
    sig = signature(f)
    args = [typestring(p[1].annotation) for p in sig.parameters.items()]
    ret = typestring(f.__closure__[0].cell_contents.returnType)
    method = "{}({}){}".format(f.__name__, ",".join(args), ret)
    return hashy(method)


# Utility function to take the string version of a method signature and
# return the 4 byte selector
def hashy(method: str) -> Bytes:
    chksum = SHA512.new(truncate="256")
    chksum.update(method.encode())
    return Bytes(chksum.digest()[:4])


def approval():
    is_app_creator = Txn.sender() == Global.creator_address()

    # Get a method selector from the python function signature, used later to route to 
    # correct subroutine
    add_sel = hashy("add(uint64,uint64)uint64")
    sub_sel = hashy("sub(uint64,uint64)uint64")
    mul_sel = hashy("mul(uint64,uint64)uint64")
    div_sel = hashy("div(uint64,uint64)uint64")
    reverse_sel = hashy("reverse(string)string")
    many_sel = hashy("manyargs(uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64,uint64)uint64")
    print(many_sel)
    qrem_sel = hashy("qrem(uint64,uint64)(uint64,uint64)")
    txn_sel = hashy("txntest(uint64,pay,uint64)uint64")
    min_sel = hashy("min_bal(account)uint64")
    concat_sel = hashy("concat_strings(string[])string")

    # Txn.application_args[0] is the method selector for the method being executed
    # compare it to known selectors below and, if match is found, call relevant subroutine
    selector = Txn.application_args[0]

    # This cond is responsible for handling the routing of methods based on their selectors
    # In the future this may be handled automatically as part of the PyTEAL contract definition
    router = Cond(
        [
            selector == add_sel,
            wrap_return(
                Itob(add(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2])))
            ),
        ],
        [
            selector == sub_sel,
            wrap_return(
                Itob(sub(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2])))
            ),
        ],
        [
            selector == mul_sel,
            wrap_return(
                Itob(mul(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2])))
            ),
        ],
        [
            selector == div_sel,
            wrap_return(
                Itob(div(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2])))
            ),
        ],
        [
            selector == qrem_sel,
            wrap_return(
                qrem(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))
            ),
        ],
        [
            selector == reverse_sel,
            wrap_return(reverse(Txn.application_args[1])),
        ],
        [
            selector == txn_sel,
            wrap_return(
                Itob(
                    txntest(
                        Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2])
                    )
                )
            ),
        ],
        [
            selector == many_sel,
            wrap_return(
                Itob(
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
                )
            ),
        ],
        [
            selector == min_sel,
            wrap_return(Itob(min_bal(Btoi(Txn.application_args[1])))),
        ],
        [
            selector == concat_sel,
            wrap_return(concat_strings(Txn.application_args[1])),
        ],
    )

    @Subroutine(TealType.uint64)
    def route_or_allow() -> Expr:
        return If(Txn.application_args.length() > Int(0)).Then(router).Else(Int(1))

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
