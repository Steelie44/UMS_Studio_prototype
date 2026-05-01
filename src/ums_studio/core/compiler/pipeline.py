from .gcode_emitter import GCodeEmitter
from .machine_profile import validate_ast_against_profile
from .native_packet_emitter import NativePacketEmitter
from ...language.parser import Parser
from ...language.tokenizer import Tokenizer
from ...language.validator import Validator


def compile_ums(source: str, machine_profile=None) -> list[object]:
    tokens = Tokenizer().tokenize(source)
    ast = Parser().parse(tokens)
    validate_ast_against_profile(ast, machine_profile)
    return Validator().validate(ast)


def compile_ums_to_gcode(source: str, target: str, machine_profile=None) -> str:
    commands = compile_ums(source, machine_profile)
    return GCodeEmitter(target).emit(commands)


def compile_ums_to_packets(source: str, target: str = "stm32f4", machine_profile=None) -> list[bytes]:
    commands = compile_ums(source, machine_profile)
    return NativePacketEmitter(target).emit(commands)
