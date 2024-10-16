def greet(*args):
    """Handle arbitrary length of args."""
    result = []
    for arg in args:
        match arg:
            case str():  # Will need a string-like test
                result.append(arg)
            case getvalue, _, _, _:  # This is an interpolation
                result.append(getvalue().upper())

    return f"{''.join(result)}!"

if __name__ == '__main__':
    print(greet"Hello {name} nice to meet you")