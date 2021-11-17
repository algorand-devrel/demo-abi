import os
from inspect import *
from typing import Callable
import hashlib

from pyteal import *



@Subroutine(TealType.uint64)
def wrap_return_bytes(b: TealType.bytes)->Expr:
    return Seq(
        Log(
            Concat(
                Bytes("base16", "0x151f7c75"), #Literally hash('return')[:4] 
                b
            )
        ),
        Int(1)
    )

@Subroutine(TealType.uint64)
def wrap_return_int(b: TealType.uint64)->Expr:
    return Seq(
        Log(
            Concat(
                Bytes("base16", "0x151f7c75"), #Literally hash('return')[:4] 
                Itob(b) 
            )
        ),
        Int(1)
    )

@Subroutine(TealType.uint64)
def add(a: TealType.uint64, b: TealType.uint64)->Expr:
    return a+b

@Subroutine(TealType.uint64)
def sub(a: TealType.uint64, b: TealType.uint64)->Expr:
    return a-b

@Subroutine(TealType.uint64)
def mul(a: TealType.uint64, b: TealType.uint64)->Expr:
    return a*b

@Subroutine(TealType.uint64)
def div(a: TealType.uint64, b: TealType.uint64)->Expr:
    return a/b

@Subroutine(TealType.uint64)
def mod(a: TealType.uint64, b: TealType.uint64)->Expr:
    return a%b

@Subroutine(TealType.bytes)
def qrem(a: TealType.uint64, b: TealType.uint64)->Expr:
    return Concat(Itob(div(a,b)), Itob(mod(a,b)))


typedict = {
    TealType.uint64:"uint64",
    TealType.bytes:"bytes",
}

def typestring(a):
    return typedict[a]

def selector(f: Callable)->str:
    sig = signature(f)
    args= [typestring(p[1].annotation) for p in sig.parameters.items()]

    ret = typestring(f.__closure__[0].cell_contents.returnType)
    if f.__name__ == "qrem":
        ret = "(uint64,uint64)"

    method = "{}({}){}".format(f.__name__, ','.join(args), ret)

    h = hashlib.new('sha512_256')
    h.update(method.encode())
    return Bytes(h.digest()[:4])


def approval():
    is_app_creator = Txn.sender() == Global.creator_address()

    add_sel = selector(add)
    sub_sel = selector(sub)
    mul_sel = selector(mul)
    div_sel = selector(div)

    qrem_sel = selector(qrem)

    router = Cond(
        [Txn.application_args[0] == add_sel, Return(wrap_return_int(add(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))))],
        [Txn.application_args[0] == sub_sel, Return(wrap_return_int(sub(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))))],
        [Txn.application_args[0] == mul_sel, Return(wrap_return_int(mul(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))))],
        [Txn.application_args[0] == div_sel, Return(wrap_return_int(div(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))))],
        [Txn.application_args[0] == qrem_sel, Return(wrap_return_bytes(qrem(Btoi(Txn.application_args[1]), Btoi(Txn.application_args[2]))))],
    )

    return Cond(
        [Txn.application_id() == Int(0),                        Return(Int(1))],
        [Txn.on_completion()  == OnComplete.DeleteApplication,  Return(is_app_creator)],
        [Txn.on_completion()  == OnComplete.UpdateApplication,  Return(is_app_creator)],
        [Txn.on_completion()  == OnComplete.CloseOut,           Return(Int(1))],
        [Txn.on_completion()  == OnComplete.OptIn,              Return(Int(1))],
        [Txn.on_completion()  == OnComplete.NoOp,               router],
    )


def clear():
    return Return(Int(1))

if __name__ == "__main__":

    path = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(path,"approval.teal"), "w") as f:
        f.write(compileTeal(approval(), mode=Mode.Application, version=5))

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(compileTeal(clear(), mode=Mode.Application, version=5))
