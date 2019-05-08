import os

from code_writer import CodeWriter
from parser import Parser


class VMTranslator:

    @staticmethod
    def translate(input_path, output_path, is_input_directory):
        """
        Top level function that translates the VM code into Hack assembly code.
        If input path is directory, translates all .vm extension file within the directory

        :param input_path: String, input path of the vm file, or path to the directory containing the vm files
        :param output_path: String, output path of the translated asm file
        :param is_input_directory: Boolean, whether input path is a path to a directory
        :return: Nothing, vm file translated
        """
        if is_input_directory:
            input_paths = [os.path.join(input_path, path)
                           for path in os.listdir(input_path) if path.endswith('.vm')]
        else:
            input_paths = [input_path]

        for i, input_path in enumerate(input_paths):
            is_first_file = i == 0
            parser = Parser(input_path=input_path)
            file_name = input_path.split('/')[-1]

            code_writer = CodeWriter(input_file_name=file_name, output_path=output_path, is_first_file=is_first_file)

            while parser.has_more_commands():
                parsed_command = parser.advance()
                code_writer.write(parsed_command)


if __name__ == '__main__':
    translator = VMTranslator()
    translator.translate('FunctionCalls/FibonacciElement',
                         'FunctionCalls/FibonacciElement/FibonacciElement.asm', True)
    translator.translate('FunctionCalls/NestedCall/Sys.vm', 'FunctionCalls/NestedCall/NestedCall.asm', False)
    translator.translate('FunctionCalls/SimpleFunction', 'FunctionCalls/SimpleFunction/SimpleFunction.asm', True)
    translator.translate('FunctionCalls/StaticsTest', 'FunctionCalls/StaticsTest/StaticsTest.asm', True)
    translator.translate('ProgramFlow/BasicLoop', 'ProgramFlow/BasicLoop/BasicLoop.asm', True)
    translator.translate('ProgramFlow/FibonacciSeries', 'ProgramFlow/FibonacciSeries/FibonacciSeries.asm', True)

    # translator.translate('MemoryAccess/BasicTest/BasicTest.vm', 'MemoryAccess/BasicTest/BasicTest.asm')
    # translator.translate('MemoryAccess/PointerTest/PointerTest.vm', 'MemoryAccess/PointerTest/PointerTest.asm')
    # translator.translate('MemoryAccess/StaticTest/StaticTest.vm', 'MemoryAccess/StaticTest/StaticTest.asm')
    # translator.translate('StackArithmetic/SimpleAdd/SimpleAdd.vm', 'StackArithmetic/SimpleAdd/SimpleAdd.asm')
    # translator.translate('StackArithmetic/StackTest/StackTest.vm', 'StackArithmetic/StackTest/StackTest.asm')
