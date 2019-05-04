from code_writer import CodeWriter
from parser import Parser


class VMTranslator:

    @staticmethod
    def translate(input_path, output_path):
        """
        Top level function that translates the VM code into Hack assembly code

        :param input_path: String, input path of the vm file
        :param output_path: String, output path of the translated asm file
        :return: Nothing, vm file translated
        """
        parser = Parser(input_path=input_path)
        file_name = input_path.split('/')[-1]
        code_writer = CodeWriter(input_file_name=file_name, output_path=output_path)
        while parser.has_more_commands():
            parsed_command = parser.advance()
            code_writer.write(parsed_command)


if __name__ == '__main__':
    translator = VMTranslator()
    translator.translate('MemoryAccess/BasicTest/BasicTest.vm', 'MemoryAccess/BasicTest/BasicTest.asm')
    translator.translate('MemoryAccess/PointerTest/PointerTest.vm', 'MemoryAccess/PointerTest/PointerTest.asm')
    translator.translate('MemoryAccess/StaticTest/StaticTest.vm', 'MemoryAccess/StaticTest/StaticTest.asm')
    translator.translate('StackArithmetic/SimpleAdd/SimpleAdd.vm', 'StackArithmetic/SimpleAdd/SimpleAdd.asm')
    translator.translate('StackArithmetic/StackTest/StackTest.vm', 'StackArithmetic/StackTest/StackTest.asm')
