from pyteal import *


is_creator = Txn.sender() == Global.creator_address()

router = Router(
    "demo-abi",
    BareCallActions(
        # On create, just approve
        no_op=OnCompleteAction.create_only(Approve()),
        # Only let creator update/delete
        update_application=OnCompleteAction.always(Return(is_creator)),
        delete_application=OnCompleteAction.always(Return(is_creator)),
        # No local state, dont bother handling it 
        close_out=OnCompleteAction.never(),
        opt_in=OnCompleteAction.never(),
        # Just be nice
        clear_state=OnCompleteAction.always(Approve()),
    ),
)

@router.method
def add(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    return output.set(a.get() + b.get())


@router.method
def sub(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    return output.set(a.get() - b.get())


@router.method
def mul(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    return output.set(a.get() * b.get())


@router.method
def div(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    return output.set(a.get() / b.get())


@router.method
def mod(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    return output.set(a.get() % b.get())


@router.method
def qrem(
    a: abi.Uint64, b: abi.Uint64, *, output: abi.Tuple2[abi.Uint64, abi.Uint64]
) -> Expr:
    return Seq(
        (q := abi.Uint64()).set(a.get() / b.get()),
        (rem := abi.Uint64()).set(a.get() % b.get()),
        output.set(q, rem),
    )


@router.method
def reverse(a: abi.String, *, output: abi.String) -> Expr:
    idx = ScratchVar()
    buff = ScratchVar()

    init = idx.store(Int(0))
    cond = idx.load() < a.length()
    iter = idx.store(idx.load() + Int(1))
    return Seq(
        buff.store(Bytes("")),
        For(init, cond, iter).Do(
            a[idx.load()].use(lambda v: buff.store(Concat(v.encode(), buff.load())))
        ),
        output.set(buff.load()),
    )


@router.method
def concat_strings(b: abi.DynamicArray[abi.String], *, output: abi.String) -> Expr:
    """
    concats strings
    sometimes does other stuff

    """

    idx = ScratchVar()
    buff = ScratchVar()

    init = idx.store(Int(0))
    cond = idx.load() < b.length()
    iter = idx.store(idx.load() + Int(1))
    return Seq(
        buff.store(Bytes("")),
        For(init, cond, iter).Do(
            b[idx.load()].use(lambda s: buff.store(Concat(buff.load(), s.get())))
        ),
        output.set(buff.load()),
    )


@router.method
def manyargs(
    a: abi.Uint64,
    b: abi.Uint64,
    c: abi.Uint64,
    d: abi.Uint64,
    e: abi.Uint64,
    f: abi.Uint64,
    g: abi.Uint64,
    h: abi.Uint64,
    i: abi.Uint64,
    j: abi.Uint64,
    k: abi.Uint64,
    l: abi.Uint64,
    m: abi.Uint64,
    n: abi.Uint64,
    o: abi.Uint64,
    p: abi.Uint64,
    q: abi.Uint64,
    r: abi.Uint64,
    s: abi.Uint64,
    t: abi.Uint64,
    *,
    output: abi.Uint64,
) -> Expr:
    """Lots of args here"""
    return output.set(a.get())


@router.method
def min_bal(acct: abi.Account, *, output: abi.Uint64):
    return output.set(MinBalance(acct.deref()))


@router.method
def txntest(amt: abi.Uint64, ptxn: abi.PaymentTransaction, fee: abi.Uint64, *, output: abi.Uint64):
    return Seq(
        Assert(ptxn.get().type_enum() == TxnType.Payment),
        Assert(ptxn.get().amount() == amt.get()),
        Assert(ptxn.get().fee() == fee.get()),
        output.set(ptxn.get().amount()),
    )


if __name__ == "__main__":
    import os
    import json

    path = os.path.dirname(os.path.abspath(__file__))

    approval, clear, contract = router.compile_program(
        version=6, optimize=OptimizeOptions(scratch_slots=True)
    )

    with open(os.path.join(path, "contract.json"), "w") as f:
        f.write(json.dumps(contract.dictify(), indent=2))

    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(approval)

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(clear)
