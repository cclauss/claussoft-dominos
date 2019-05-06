#!/usr/bin/env python3

try:
    input = raw_input  # Python 2
except NameError:  # Python 3
    pass


def askNumberFromOneTo(inMax):
    intMax = int(inMax)
    if intMax < 1:
        return 1
    # print('inMax:', inMax, 'intMax:', intMax)
    print("Enter a number from 1 to {}: ".format(inMax))
    s = input("Enter a number from 1 to {}: ".format(intMax)).lower()
    assert s[0] != "q"
    if s[0] == "u":
        return s[0]
    try:
        i = int(float(s))
    except:
        i = 0
    print("s:", s, "i:", i)
    return i if 1 <= i <= intMax else askNumberFromOneTo(intMax)


def main():
    print("Got: {}".format(askNumberFromOneTo(10.34)))


if __name__ == "__main__":
    main()
