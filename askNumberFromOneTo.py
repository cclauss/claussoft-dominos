#!/usr/bin/env python3


def ask_number_from_one_to(maximum: int):
    if maximum < 1:
        return 1
    s = input(f"Enter a number from 1 to {maximum}: ").strip().lower()
    assert s[0] != "q", "User wants to quit."
    if s[0] == "u":  # Undo
        return s[0]
    try:
        i = int(float(s))
    except ValueError:
        i = 0
    print(f"s: {s}, i: {i}")
    return i if 1 <= i <= maximum else ask_number_from_one_to(maximum)


def main():
    print(f"Got: {ask_number_from_one_to(10.34)}")


if __name__ == "__main__":
    main()
