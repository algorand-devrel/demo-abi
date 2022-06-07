from pyteal import *


# Create a simple Expression to use later
is_creator = Txn.sender() == Global.creator_address()

# Main router class
router = Router(
    # Name of the contract
    "demo-abi",
    # What to do for each on-complete type when no arguments are passed (bare call)
    BareCallActions(
        # On create only, just approve
        no_op=OnCompleteAction.create_only(Approve()),
        # Always let creator update/delete
        update_application=OnCompleteAction.always(Return(is_creator)),
        delete_application=OnCompleteAction.always(Return(is_creator)),
        # No local state, dont bother handling it
        close_out=OnCompleteAction.never(),
        opt_in=OnCompleteAction.never(),
        # Just be nice, we _must_ provide _something_ for clear state becuase it is its own
        # program and the router needs _something_ to build
        clear_state=OnCompleteAction.always(Approve()),
    ),
)

# This decorator lets you add a new method to be handled by the router
# this will generate a method with signature `add(uint64,uint64)uint64`
# and route matching app call transactions here
@router.method
def add(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    # The doc string is used in the `descr` field of the resulting Method
    """add sums two uint64s and returns the result"""

    # a.get() and b.get() return expressions to
    # load the scratch vars underlying the ABI types on the stack

    # output.set(...) stores the result of the expression into
    # the scratch var that underlies the output type

    # whatever `output` is set to will be "returned" from the
    # app call, properly encoded according to its type and will have the
    # ABI return prefix prepended to the logged message
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
        # Use walrus operator to declare a new variable
        # then set its value, since set returns an expression
        # it is legal to include in a seq
        (q := abi.Uint64()).set(a.get() / b.get()),
        (rem := abi.Uint64()).set(a.get() % b.get()),
        # Here we're setting the value on a tuple[uint64, uint64]
        # So pass them each in to the set method
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
            # a is a `string`, which is a byte[] or dynamic array of bytes
            # we can access individual bytes with the square bracket notation
            # this returns a ComputedValue[T] having methods `use` and `store_into`
            # `use` is passed a lambda that "unwraps" the underlying ABI type, allowing us to
            # use it as we might expect for `abi.Byte`. Since we want to treat the Byte as a bytestring
            # we just use encode to marshal it out to bytestring, using `.get()` would return a uint64
            a[idx.load()].use(lambda v: buff.store(Concat(v.encode(), buff.load())))
            # Using store_into would take an abi type we want to put the value in. You may also
            # pass a ComputedValue[T] in to an appropriate `set` method and it uses `store_into` under the covers
            # ex: (b := abi.Byte()).set(a[idx.load()])
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
            # Similar to `abi.String` type in the previous method, b[idx.load()] returns
            # a ComputedValue[T], since we want the String we can just use `s.get()` here to
            # dump out the bytes
            b[idx.load()].use(lambda s: buff.store(Concat(buff.load(), s.get())))
        ),
        output.set(buff.load()),
    )

@router.method
def sum_array(a: abi.DynamicArray[abi.Uint64], *, output: abi.Uint64)->Expr:
    idx = ScratchVar()

    init = idx.store(Int(0))
    cond = idx.load() < a.length()
    iter = idx.store(idx.load() + Int(1))

    return Seq(
        (running_sum := ScratchVar()).store(Int(0)),
        For(init, cond, iter).Do(
            Seq(
                # Similar to above, but we're using `set` to initialize curr_value 
                # with the ComputedValue[Uint64] instead of using the `use` method
                (curr_val := abi.Uint64()).set(a[idx.load()]),
                running_sum.store(curr_val.get() + running_sum.load())
            )
        ),
        output.set(running_sum.load())
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
    # acct is a `reference` type, using `acct.get()` will return
    # the index of the acct passed, while `acct.deref()` will look up
    # the value in the appropriate Transaction Array
    # this is the same pattern for Account/Asset/Application types
    return output.set(MinBalance(acct.get()))


@router.method
def txntest(
    amt: abi.Uint64,
    ptxn: abi.PaymentTransaction,
    fee: abi.Uint64,
    *,
    output: abi.Uint64,
):
    # Transaction types may be specified but aren't part of the application arguments
    # you can get the underlying TxnObject with ptxn.get() and perform all the expected
    # functions on it to get access to the fields
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

    # we use compile program here to get the resulting teal code and Contract definition
    # similarly we could use build_program to return the AST for approval/clear and compile it
    # ourselves, but why?
    approval, clear, contract = router.compile_program(
        version=6, optimize=OptimizeOptions(scratch_slots=True)
    )

    # Dump out the contract as json that can be read in by any of the SDKs
    with open(os.path.join(path, "contract.json"), "w") as f:
        f.write(json.dumps(contract.dictify(), indent=2))

    # Write out the approval and clear programs
    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(approval)

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(clear)
