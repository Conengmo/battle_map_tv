import threading


def debounce(wait):
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)

            if hasattr(debounced, "_timer"):
                debounced._timer.cancel()
            debounced._timer = threading.Timer(wait, call_it)  # type: ignore
            debounced._timer.start()  # type: ignore

        return debounced

    return decorator
