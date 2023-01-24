from typing import Literal
from pyteal import (
    Approve,
    BareCallActions,
    Concat,
    Expr,
    Int,
    OnCompleteAction,
    Router,
    ScratchVar,
    Seq,
    abi,
    Itob,
    Suffix,
    Len,
    ExtractUint16,
    While,
)

# util method for converting an Int to u16 bytes
def to_u16(i: Expr):
    return Suffix(Itob(i), Int(6))


router = Router(
    "demo-abi-types",
    BareCallActions(
        no_op=OnCompleteAction.create_only(Approve()),
        update_application=OnCompleteAction.always(Approve()),
        delete_application=OnCompleteAction.always(Approve()),
        clear_state=OnCompleteAction.call_only(Approve()),
    ),
)


# While its not adivsable to make heavy use dynamic ABI
# types within the logic of the contract due to the inefficient
# access to elements, below are some examples of how you
# might construct a larger array from 2 smaller ones


@router.method
def concat_static_arrays(
    a: abi.StaticArray[abi.Uint64, Literal[3]],
    b: abi.StaticArray[abi.Uint64, Literal[3]],
    *,
    output: abi.StaticArray[abi.Uint64, Literal[6]],
):
    # Static arrays are easy to concat since there is no
    # length prefix or offsets to track. The typing of the
    # value includes the length explicitly.
    return output.decode(Concat(a.encode(), b.encode()))


@router.method
def concat_dynamic_arrays(
    a: abi.DynamicArray[abi.Uint64],
    b: abi.DynamicArray[abi.Uint64],
    *,
    output: abi.DynamicArray[abi.Uint64],
):
    """demonstrate how two dynamic arrays of static elements could be concat'd"""
    # A Dynamic array of static types is encoded as:
    # [uint16 length, element 0, element 1]
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
def concat_dynamic_string_arrays(
    a: abi.DynamicArray[abi.String],
    b: abi.DynamicArray[abi.String],
    *,
    output: abi.DynamicArray[abi.String],
):
    """demonstrate how two dynamic arrays of dynamic elements could be concat'd"""
    # NOTE: this is not efficient (clearly), static types should
    # always be preferred if possible. Otherwise use some encoding
    # other than the abi encoding, which is more for serializing/deserializing data

    # A Dynamic array of dynamic types is encoded as:
    # [uint16 length, uint16 pos elem 0, uint16 pos elem 1, elem 0, elem 1]
    # so to concat them, we must remove the 2 byte length prefix
    # from each, and prepend the new length (of elements!) as 2 byte integer
    return Seq(
        # Make a couple bufs for the header (offsets) and elements
        (_head_buf := ScratchVar()).store(
            Suffix(Itob(a.length() + b.length()), Int(6))
        ),
        # Take the element contents of the 2 arrays
        (_tail_buf := ScratchVar()).store(
            Concat(
                # strip length and positions, now its [elem0, elem1, elem2]
                Suffix(a.encode(), Int(2) + (Int(2) * a.length())),
                Suffix(b.encode(), Int(2) + (Int(2) * b.length())),
            )
        ),
        # Create the offset value we'll use for the position header
        # we know the first string will start at 2 * combined length
        (offset := ScratchVar()).store(((a.length() + b.length()) * Int(2))),
        # We'll track the current string we're working on here
        (curr_str_len := ScratchVar()).store(Int(0)),
        (cursor := ScratchVar()).store(Int(0)),
        While((cursor.load() + curr_str_len.load()) <= Len(_tail_buf.load())).Do(
            # Add the offset for this string to the head buf
            _head_buf.store(Concat(_head_buf.load(), to_u16(offset.load()))),
            # Get the length of the current string + 2 bytes for uint16 len
            curr_str_len.store(ExtractUint16(_tail_buf.load(), cursor.load()) + Int(2)),
            # update our cursor to point to the next str element
            cursor.store(cursor.load() + curr_str_len.load()),
            # update our offset similarly
            offset.store(offset.load() + curr_str_len.load()),
        ),
        output.decode(Concat(_head_buf.load(), _tail_buf.load())),
    )


class Order(abi.NamedTuple):
    item: abi.Field[abi.Uint64]
    amount: abi.Field[abi.Uint32]
    note: abi.Field[abi.String]


@router.method
def place_order(o: Order):
    pass
