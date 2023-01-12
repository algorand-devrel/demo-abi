from typing import Literal
from pyteal import (
    Approve,
    Assert,
    BareCallActions,
    Bytes,
    Concat,
    Expr,
    For,
    Global,
    Int,
    OnCompleteAction,
    OptimizeOptions,
    Return,
    Router,
    ScratchVar,
    Seq,
    Txn,
    TxnType,
    abi,
    Itob,
    Suffix,
)


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
        # Always let creator update/delete but only by the creator of this contract
        update_application=OnCompleteAction.always(Return(is_creator)),
        delete_application=OnCompleteAction.always(Return(is_creator)),
        # No local state, dont bother handling it
        # close_out=OnCompleteAction.never(),
        # opt_in=OnCompleteAction.never(),
        # Just be nice, we _must_ provide _something_ for clear state
        # becuase it is its own program and the router needs _something_ to build
        # clear_state=OnCompleteAction.call_only(Approve()),
        clear_state=OnCompleteAction.never(),
    ),
)

# This decorator lets you add a new method to be handled by the router
# this will generate a method with signature `add(uint64,uint64)uint64`
# and route matching app call transactions here
@router.method
def add(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    # The doc string is used in the `descr` field of the resulting Method
    """sum a and b, return the result"""

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
    """subtract b from a, return the result"""
    return output.set(a.get() - b.get())


@router.method
def mul(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """multiply a and b, return the result"""
    return output.set(a.get() * b.get())


@router.method
def div(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """divide a by b, return the result"""
    return output.set(a.get() / b.get())


@router.method
def mod(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
    """modulo of a by b, return the result"""
    return output.set(a.get() % b.get())


class Qrem_result(abi.NamedTuple):
    quantity: abi.Field[abi.Uint64]
    remainder: abi.Field[abi.Uint64]


@router.method
def qrem(a: abi.Uint64, b: abi.Uint64, *, output: Qrem_result) -> Expr:
    """divide a by b, and modulo of a by b, return the results as a tuple"""
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
    """reverse the string a, return the result"""
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
            # `use` is passed a lambda that "unwraps" the underlying ABI type,
            # allowing us to use it as we might expect for `abi.Byte`. Since we want
            # to treat the Byte as a bytestring we just use encode to marshal it out
            # to bytestring, using `.get()` would return a uint64
            a[idx.load()].use(lambda v: buff.store(Concat(v.encode(), buff.load())))
            # Using store_into would take an abi type we want to put the value in.
            # You may also pass a ComputedValue[T] in to an appropriate `set` method
            # which uses `store_into` under the covers
            # ex: (b := abi.Byte()).set(a[idx.load()])
        ),
        output.set(buff.load()),
    )


@router.method
def concat_strings(b: abi.DynamicArray[abi.String], *, output: abi.String) -> Expr:
    """Accept a list of strings, return the result of concating them all"""

    idx = ScratchVar()
    buff = ScratchVar()

    init = idx.store(Int(0))
    cond = idx.load() < b.length()
    iter = idx.store(idx.load() + Int(1))
    return Seq(
        buff.store(Bytes("")),
        For(init, cond, iter).Do(
            # Similar to `abi.String` type in the previous method, b[idx.load()]
            # returns a ComputedValue[T], since we want the String we
            # can just use `s.get()` here to
            # dump out the bytes
            b[idx.load()].use(lambda s: buff.store(Concat(buff.load(), s.get())))
        ),
        output.set(buff.load()),
    )


@router.method
def make_array(
    a: abi.Uint64, b: abi.Uint64, c: abi.Uint64, *, output: abi.DynamicArray[abi.Uint64]
) -> Expr:
    return Seq(output.set([a, b, c]))


@router.method
def sum_array(a: abi.DynamicArray[abi.Uint64], *, output: abi.Uint64) -> Expr:
    """Accept a list of uint64, return the result of summing them all"""
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
                running_sum.store(curr_val.get() + running_sum.load()),
            )
        ),
        output.set(running_sum.load()),
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
    """Lots of args here, internally they get tuple'd after the 15th arg,
    but atc and router handles this for us"""
    return output.set(a.get())


@router.method
def min_bal(acct: abi.Account, *, output: abi.Uint64):
    """Return the minimum balance for the passed account"""
    # acct is a `reference` type and is passed in the `accounts`
    # array of the transaction # this lets us look up information about the
    # account or send to the account from some inner transaction
    # using `acct.address()` will return the address of the account and
    # `acct.params()` returns a parameters object to inspect other fields
    # this is a similar pattern for Account/Asset/Application types
    return Seq(mb := acct.params().min_balance(), output.set(mb.value()))


@router.method
def no_return(a: abi.Uint64):
    """
    Just a demonstration of no return value or `void`
    Omit the `*, output: abi...` from the method signature
    and void will be used as the return value
    """
    return Assert(Int(1))


@router.method
def txntest(
    amt: abi.Uint64,
    ptxn: abi.PaymentTransaction,
    fee: abi.Uint64,
    *,
    output: abi.Uint64,
):
    """Useless method that just demonstrates specifying a
    transaction in the method signature"""
    # Transaction types may be specified but aren't part of the application arguments
    # you can get the underlying TxnObject with ptxn.get() and perform all the expected
    # functions on it to get access to the fields

    return Seq(
        Assert(ptxn.get().type_enum() == TxnType.Payment),
        Assert(ptxn.get().amount() == amt.get()),
        Assert(ptxn.get().fee() == fee.get()),
        output.set(ptxn.get().amount()),
    )


@router.method
def concat_dynamic_arrays(
    a: abi.DynamicArray[abi.Uint64],
    b: abi.DynamicArray[abi.Uint64],
    *,
    output: abi.DynamicArray[abi.Uint64],
):
    """demonstrate how two dynamic arrays could be concatt'd"""
    # A Dynamic array of static types is encoded as:
    # [uint16 length][element 0][element 1]...
    # so to concat them, we must remove the 2 byte length prefix
    # from each, and prepend the new length (of elements!) as 2 byte integer
    return output.decode(
        Concat(
            Suffix(Itob(a.length() + b.length()), Int(6)),
            Suffix(a.encode(), Int(2)),
            Suffix(b.encode(), Int(2)),
        )
    )


@router.method
def concat_static_arrays(
    a: abi.StaticArray[abi.Uint64, Literal[3]],
    b: abi.StaticArray[abi.Uint64, Literal[3]],
    *,
    output: abi.StaticArray[abi.Uint64, Literal[6]],
):
    # Static arrays are easier to concat since there is no
    # length prefix. The typing of the value includes the length
    # explicitly.
    return output.decode(Concat(a.encode(), b.encode()))


if __name__ == "__main__":
    import os
    import json

    path = os.path.dirname(os.path.abspath(__file__))

    # we use compile program here to get the resulting teal code
    # and Contract definition, similarly we could use build_program
    # to return the AST for approval/clear and compile it
    # ourselves, but why?
    approval, clear, contract = router.compile_program(
        version=8, optimize=OptimizeOptions(scratch_slots=True)
    )

    # Dump out the contract as json that can be read in by any of the SDKs
    with open(os.path.join(path, "contract.json"), "w") as f:
        f.write(json.dumps(contract.dictify(), indent=2))

    # Write out the approval and clear programs
    with open(os.path.join(path, "approval.teal"), "w") as f:
        f.write(approval)

    with open(os.path.join(path, "clear.teal"), "w") as f:
        f.write(clear)
