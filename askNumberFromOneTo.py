#!/usr/bin/env python3


def askNumberFromOneTo(inMax):
    intMax = int(inMax)
    if intMax < 1:
        return 1
    s = input(f"Enter a number from 1 to {intMax}: ").strip().lower()
    assert s[0] != "q", "User wants to quit."
    if s[0] == "u":  # Undo
        return s[0]
    try:
        i = int(float(s))
    except ValueError:
        i = 0
    print(f"s: {s}, i: {i}")
    return i if 1 <= i <= intMax else askNumberFromOneTo(intMax)


def main():
    print(f"Got: {askNumberFromOneTo(10.34)}")


if __name__ == "__main__":
    main()
