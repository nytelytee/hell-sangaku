from __future__ import annotations

import builtins
import sys
from functools import cache
from time import perf_counter_ns
from types import TracebackType
from typing import (TYPE_CHECKING, Callable, Literal, Protocol, Self, TextIO,
                    TypeVar, cast, overload)

if TYPE_CHECKING:
    from _typeshed import SupportsFlush, SupportsWrite
    _T_contra = TypeVar("_T_contra", contravariant=True)
    class _SupportsWriteAndFlush(
        SupportsWrite[_T_contra],
        SupportsFlush,
        Protocol[_T_contra]
    ): ...

    class PrintFunction(Protocol):

        @overload
        def __call__(
            self,
            *values: object,
            sep: str | None = " ",
            end: str | None = "\n",
            file: SupportsWrite[str] | None = None,
            flush: Literal[False] = False,
        ) -> None: ...

        @overload
        def __call__(
            self,
            *values: object,
            sep: str | None = " ",
            end: str | None = "\n",
            file: _SupportsWriteAndFlush[str] | None = None,
            flush: bool
        ) -> None: ...


def format_time(time_ns: int) -> str:
    time = time_ns / 10**9
    time, time_s = divmod(time, 60)
    time_h, time_m = divmod(time, 60)
    return (f"{'{:02d}h'.format(int(time_h)) if time_h else ''}"
            f"{'{:02d}m'.format(int(time_m)) if time_m or time_h else ''}"
            f"{'{:06.3f}s'.format(time_s) if time_s else '00.000s'}")


class Timer:

    subtimers: list[tuple[str, int]]
    subtimer_types: list[Literal['manual', 'context-manager']]
    state: Literal['newline', 'inline-noinfoline', 'inline-infoline']
    last_printed_line: str
    padding_function: Callable[[int, Timer], str]
    subtimer_name_format: Callable[[str, Timer], str]
    subtimer_name_format_inline: Callable[[str, Timer], str]
    time_format: Callable[[int, Timer], str]
    time_format_inline: Callable[[int, Timer], str]
    prefix: str
    suffix: str
    waiting_suffix: str
    inline_prefix: str
    inline_suffix: str
    inline_waiting_suffix: str
    noinfoline_separator: str
    infoline_is_inline: bool
    noinfoline_is_inline: bool
    newline: bool
    _print: PrintFunction
    _print_overridden: bool

    class TimerError(Exception):
        pass

    class TimerContextManager:

        name: str
        subtimers: Timer

        def __init__(self, name: str, subtimers: Timer, /) -> None:
            self.name = name
            self.subtimers = subtimers

        def __enter__(self, /) -> None:
            self.subtimers.subtimer_types.append('context-manager')
            self.subtimers._push(self.name)

        @overload
        def __exit__(
            self, exc_type: None, exc_val: None, exc_tb: None, /,
        ) -> None:
            ...

        @overload
        def __exit__(
            self,
            exc_type: type[BaseException],
            exc_val: BaseException,
            exc_tb: TracebackType,
            /,
        ) -> None:
            ...

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
            /,
        ) -> None:
            if exc_type is not None:
                return
            if self.subtimers.subtimer_types[-1] != 'context-manager':
                raise self.subtimers.TimerError(
                    "Unpopped manual subtimers in context."
                )
            del self.subtimers.subtimer_types[-1]
            self.subtimers._pop()

    def __init__(
        self, /,
        padding: str | Callable[[int, Timer], str] = '│  ',
        subtimer_name_format: Callable[[str, Timer], str] = (
            lambda subtimer_name, subtimers: '┌► ' + subtimer_name
        ),
        subtimer_name_format_inline: Callable[[str, Timer], str] = (
            lambda subtimer_name, subtimers: subtimer_name
        ),
        time_format: Callable[[int, Timer], str] = (
            lambda time_ns, subtimers: format_time(time_ns)
        ),
        time_format_inline: Callable[[int, Timer], str] = (
            lambda time_ns, subtimers: format_time(time_ns)
        ),
        inline_prefix: str = ' ══► ',
        inline_suffix: str = ' ──► ',
        inline_waiting_suffix: str = ' --> ',
        noinfoline_separator: str = ' ──► ',
        prefix: str = '',
        suffix: str = '└► ',
        waiting_suffix: str = '└> ',
        infoline_is_inline: bool = True,
        noinfoline_is_inline: bool = True
    ) -> None:
        self.subtimers = []
        self.subtimer_types = []
        self.state = 'newline'
        self.last_printed_line = ''
        def default_padding_function(level: int, _subtimers: Timer) -> str:
            return level*cast(str, padding)
        self.padding_function = (
            padding
            if callable(padding) else
            cache(default_padding_function)
        )
        self.subtimer_name_format = subtimer_name_format
        self.subtimer_name_format_inline = subtimer_name_format_inline
        self.time_format = time_format
        self.time_format_inline = time_format_inline
        self.inline_prefix = inline_prefix
        self.inline_suffix = inline_suffix
        self.inline_waiting_suffix = inline_waiting_suffix
        self.noinfoline_separator = noinfoline_separator
        self.prefix = prefix
        self.suffix = suffix
        self.waiting_suffix = waiting_suffix
        self.infoline_is_inline = noinfoline_is_inline and infoline_is_inline
        self.noinfoline_is_inline = noinfoline_is_inline
        self.newline = False
        self._print = builtins.print
        self._print_overridden = False

    def __enter__(self, /) -> Self:
        if self._print_overridden:
            raise self.TimerError(
                "Can't override print multiple times (nested?)."
            )
        self._print_overridden = True
        self._print = builtins.print
        builtins.print = self.print
        return self

    @overload
    def __exit__(
        self, exc_type: None, exc_val: None, exc_tb: None, /,
    ) -> None:
        ...

    @overload
    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
        /,
    ) -> None:
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
        /,
    ) -> None:
        if not self._print_overridden:
            raise self.TimerError(
                "Print not overridden (manually called __exit__?)."
            )
        builtins.print = self._print
        self._print_overridden = False
    
    def override_print(self, /) -> None:
        if self._print_overridden:
            raise self.TimerError("Can't override print multiple times.")
        self._print_overridden = True
        self._print = builtins.print
        builtins.print = self.print

    def unoverride_print(self) -> None:
        if not self._print_overridden:
            raise self.TimerError("Print not overridden.")
        builtins.print = self._print
        self._print_overridden = False

    def _push(self, subtimer_name: str, /) -> None:
        if len(self.subtimers) == 0 and self.newline:
            self.newline = False
            self._print()
        padding = self.padding_function(len(self.subtimers), self)
        prev_padding = self.padding_function(len(self.subtimers) - 1, self)
        prefix = self.prefix.replace(
            '{padding}', padding
        ).replace(
            '{prev_padding}', prev_padding
        )
        waiting_suffix = self.waiting_suffix.replace(
            '{next_padding}', padding
        ).replace(
            '{padding}', prev_padding
        )
        clear = '\33[2K\r'
        match self.state:
            case 'newline':
                pass
            case 'inline-infoline':
                name = self.subtimers[-1][0]
                self._print(
                    f"{clear}{prev_padding}"
                    f"{self.subtimer_name_format(name, self)}{prefix}\n"
                    f"{padding}{self.last_printed_line}"
                )
            case 'inline-noinfoline':
                name = self.subtimers[-1][0]
                self._print(
                    f"{clear}{prev_padding}"
                    f"{self.subtimer_name_format(name, self)}{prefix}"
                )
        if self.noinfoline_is_inline:
            self._print(
                f"{clear}{padding}"
                f"{self.subtimer_name_format_inline(subtimer_name, self)}"
                f"{self.inline_waiting_suffix}", end='', flush=True
            )
            self.state = 'inline-noinfoline'
        else:
            self._print(
                f"{clear}{padding}"
                f"{self.subtimer_name_format(subtimer_name, self)}{prefix}"
                f"\n{padding}{waiting_suffix}", end='', flush=True
            )
            self.state = 'newline'
        self.subtimers.append((subtimer_name, perf_counter_ns()))

    def _pop(self, /) -> None:
        prev_padding = self.padding_function(len(self.subtimers), self)
        name, timer = self.subtimers.pop()
        padding = self.padding_function(len(self.subtimers), self)
        waiting_padding = self.padding_function(len(self.subtimers) - 1, self)
        clear = '\33[2K\r'
        waiting_suffix = self.waiting_suffix.replace(
            '{next_padding}', padding
        ).replace(
            '{padding}', waiting_padding
        )
        match self.state:
            case 'newline':
                suffix = self.suffix.replace(
                    '{padding}', padding
                ).replace(
                    '{next_padding}', prev_padding
                )
                self._print(
                    f"{clear}{padding}{suffix}"
                    f"{self.time_format(perf_counter_ns() - timer, self)}"
                    f"\n{waiting_padding}{waiting_suffix}",
                    end='', flush=True
                )
            case 'inline-infoline':
                self._print(
                    f"{clear}{padding}"
                    f"{self.subtimer_name_format_inline(name, self)}"
                    f"{self.inline_prefix}"
                    f"{self.last_printed_line}"
                    f"{self.inline_suffix}"
                    f"{self.time_format_inline(perf_counter_ns()-timer, self)}"
                    f"\n{waiting_padding}{waiting_suffix}",
                    end='', flush=True
                )
            case 'inline-noinfoline':
                self._print(
                    f"{clear}{padding}"
                    f"{self.subtimer_name_format_inline(name, self)}"
                    f"{self.noinfoline_separator}"
                    f"{self.time_format_inline(perf_counter_ns()-timer, self)}"
                    f"\n{waiting_padding}{waiting_suffix}",
                    end='', flush=True
                )
        if not len(self.subtimers):
            self._print(clear, end='')
        self.state = 'newline'
        self.newline = len(self.subtimers) > 0

    def push(self, subtimer_name: str, /) -> None:
        self.subtimer_types.append('manual')
        self._push(subtimer_name)

    def pushed(
        self, subtimer_name: str, /,
    ) -> Timer.TimerContextManager:
        return self.TimerContextManager(subtimer_name, self)

    def pop(self, /) -> None:
        if self.subtimer_types[-1] != 'manual':
            raise self.TimerError(
                "Cannot pop context manager subtimer manaully."
            )
        del self.subtimer_types[-1]
        self._pop()

    def print(
        self, /,
        *values: object,
        sep: str | None = ' ',
        end: str | None = '\n',
        file: TextIO | None = None,
        flush: bool = False,
    ) -> None:
        sep = ' ' if sep is None else sep
        end = '\n' if end is None else end
        # we are not printing to stdout, just call the overloaded print
        if file is not None and file is not sys.stdout:
            return self._print(
                *values, sep=sep, end=end, file=file, flush=False
            )
        # we are not inside a subtimer, just call the overloaded print
        if len(self.subtimers) == 0:
            return self._print(
                *values, sep=sep, end=end, file=file, flush=flush
            )
        padding = self.padding_function(len(self.subtimers), self)
        prev_padding = self.padding_function(len(self.subtimers) - 1, self)
        clear = '\33[2K\r'
        if (self.state == 'inline-noinfoline' and not self.infoline_is_inline):
            prefix = self.prefix.replace(
                '{padding}', padding
            ).replace(
                '{prev_padding}', prev_padding
            )
            name = self.subtimers[-1][0]
            self._print(
                f"{clear}{prev_padding}"
                f"{self.subtimer_name_format(name, self)}{prefix}"
            )
            self.state = 'newline'

        strings = (sep.join(str(o) for o in values) + end).split('\n')
        for i, content in enumerate(strings, 0):
            is_last = (i == len(strings)-1)
            if is_last and content == '':
                self.newline = True
                break
            elif is_last and content != '':
                self.newline = False
            match self.state:
                case 'newline':
                    waiting_suffix = self.waiting_suffix.replace(
                        '{next_padding}', padding
                    ).replace(
                        '{padding}', prev_padding
                    ) if len(self.subtimers) > 0 else ''
                    if self.newline:
                        self._print(
                            f"{clear}{padding}{content}"
                            f"\n{prev_padding}{waiting_suffix}",
                            end='', flush=True
                        )
                        self.last_printed_line = content
                    else:
                        self._print(
                            f"{clear}{padding}"
                            f"{self.last_printed_line}{content}"
                            f"{self.inline_waiting_suffix}",
                            end='', flush=True
                        )
                        self.newline = True
                        self.last_printed_line = self.last_printed_line+content
                    self.state = 'newline'
                case 'inline-infoline':
                    name = self.subtimers[-1][0]
                    prefix = self.prefix.replace(
                        '{padding}', padding
                    ).replace(
                        '{prev_padding}', prev_padding
                    )
                    waiting_suffix = self.waiting_suffix.replace(
                        '{next_padding}', padding
                    ).replace(
                        '{padding}', prev_padding
                    )
                    if self.newline:
                        self._print(
                            f"{clear}{prev_padding}"
                            f"{self.subtimer_name_format(name, self)}"
                            f"{prefix}\n{padding}{self.last_printed_line}\n"
                            f"{padding}{content}"
                            f"\n{prev_padding}{waiting_suffix}",
                            end='', flush=True
                        )
                        self.state = 'newline'
                        self.last_printed_line = content
                    else:
                        self._print(
                            f"{clear}{prev_padding}"
                            f"{self.subtimer_name_format_inline(name, self)}"
                            f"{self.inline_prefix}{self.last_printed_line}"
                            f"{content}{self.inline_waiting_suffix}",
                            end='', flush=True
                        )
                        self.state = 'inline-infoline'
                        self.newline = True
                        self.last_printed_line = self.last_printed_line+content
                case 'inline-noinfoline':
                    name = self.subtimers[-1][0]
                    self._print(
                        f"{clear}{prev_padding}"
                        f"{self.subtimer_name_format_inline(name, self)}"
                        f"{self.inline_prefix}{content}"
                        f"{self.inline_waiting_suffix}",
                        end='',
                        flush=True
                    )
                    self.newline = True
                    self.state = 'inline-infoline'
                    self.last_printed_line = content
