import re
import unittest
from ..parsing.Parser import Parser


class TestParsing(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = Parser()
    
    def tearDown(self):
        self.parser.clear()

    def test_add(self):
        expected = '00000000010001000011000000000000'
        actual = str(self.parser.parse_line('add $1, $r2, $3;', 1))
        self.assertEqual(expected, actual, 'add failed')

    def test_sub(self):
        expected = '00000000010001000011000000000100'
        actual = str(self.parser.parse_line('sub $1, $r2, $3;', 1))
        self.assertEqual(expected, actual, 'sub failed')

    def test_addi(self):
        expected = '00101000010000100000000000000001'
        actual = str(self.parser.parse_line('addi $1, $r1   1;', 1))
        self.assertEqual(expected, actual, 'addi positive failed')
        expected = '00101000010000111111111111111111'
        actual = str(self.parser.parse_line('addi $1, $r1   -1;', 1))
        self.assertEqual(expected, actual, 'addi negative failed')

    def test_or(self):
        expected = '00000000010000000110000000001100'
        actual = str(self.parser.parse_line('or $1, $r0   $6;', 1))
        self.assertEqual(expected, actual, 'or failed')

    def test_and(self):
        expected = '00000000010000000110000000001000'
        actual = str(self.parser.parse_line('and $1, $r0   $6;', 1))
        self.assertEqual(expected, actual, 'and failed')

    def test_sll(self):
        expected = '00000000010000100000001000010000'
        actual = str(self.parser.parse_line('sll $1, $r1   4;', 1))
        self.assertEqual(expected, actual, 'sll failed')
        with self.assertRaises(AssertionError, msg='Test negative shift failed: sll'):
            self.parser.parse_line('sll $1 $2 -1', 1)

    def test_sra(self):
        expected = '00000000010000100000001000010100'
        actual = str(self.parser.parse_line('sra $1, $r1   4;', 1))
        self.assertEqual(expected, actual, 'sll failed')
        with self.assertRaises(AssertionError, msg='Test negative shift failed: sra'):
            self.parser.parse_line('sra $1 $2 -1', 1)

    def test_mul(self):
        expected = '00000000010000000110000000011000'
        actual = str(self.parser.parse_line('mul $1, $r0   $6;', 1))
        self.assertEqual(expected, actual, 'mul failed')
        actual = str(self.parser.parse_line('mult $1, $r0   $6;', 1))
        self.assertEqual(expected, actual, 'mult failed')

    def test_div(self):
        expected = '00000000010000000110000000011100'
        actual = str(self.parser.parse_line('div $1, $r0   $6;', 1))
        self.assertEqual(expected, actual, 'div failed')

    def test_sw(self):
        expected = '00111000010001000000000000000001'
        actual = str(self.parser.parse_line('sw $1, 1($2);', 1))
        self.assertEqual(expected, actual, 'sw failed')
        expected = '00111000010001011111111111111111'
        actual = str(self.parser.parse_line('sw $1, -1($2);', 1))
        self.assertEqual(expected, actual, 'sw failed')

    def test_lw(self):
        expected = '01000000010001000000000000000001'
        actual = str(self.parser.parse_line('lw $1, 1($2);', 1))
        self.assertEqual(expected, actual, 'sw failed')
        expected = '01000000010001011111111111111111'
        actual = str(self.parser.parse_line('lw $1, -1($2);', 1))
        self.assertEqual(expected, actual, 'sw failed')

    def test_j(self):
        expected = '00001000000000000000000000001010'
        actual = str(self.parser.parse_line('j 10;', 1))
        str(self.assertEqual(expected, actual, 'j failed'))
        with self.assertRaises(AssertionError, msg='Test negative T failed: j'):
            self.parser.parse_line('j -10;', 1)

    def test_bne(self):
        expected = '00010000010001000000000000001010'
        actual = str(self.parser.parse_line('bne $1, $2, 10;', 1))
        self.assertEqual(expected, actual, 'bne failed')
        expected = '00010000010001011111111111110110'
        actual = str(self.parser.parse_line('bne $1, $2, -10;', 1))
        self.assertEqual(expected, actual, 'bne failed for negative')

    def test_jal(self):
        expected = '00011000000000000000000000001010'
        actual = str(self.parser.parse_line('jal 10;', 1))
        self.assertEqual(expected, actual, 'jal failed')
        with self.assertRaises(AssertionError, msg='Test negative T failed: jal'):
            self.parser.parse_line('jal -10;', 1)

    def test_jr(self):
        expected = '00100111110000000000000000000000'
        actual = str(self.parser.parse_line('jr $31;', 1))
        self.assertEqual(expected, actual, 'jr failed')

    def test_blt(self):
        expected = '00110000010001000000000000001010'
        actual = str(self.parser.parse_line('blt $1, $2, 10;', 1))
        self.assertEqual(expected, actual, 'blt failed')
        expected = '00110000010001011111111111110110'
        actual = str(self.parser.parse_line('blt $1, $2, -10;', 1))
        self.assertEqual(expected, actual, 'blt failed for negative')

    def test_bex(self):
        expected = '10110000000000000000000000001010'
        actual = str(self.parser.parse_line('bex 10;', 1))
        self.assertEqual(expected, actual, 'bex failed')
        with self.assertRaises(AssertionError, msg='Test negative T failed: bex'):
            self.parser.parse_line('bex -10;', 1)

    def test_setx(self):
        expected = '10101000000000000000000000001010'
        actual = str(self.parser.parse_line('setx 10;', 1))
        self.assertEqual(expected, actual, 'setx failed')
        with self.assertRaises(AssertionError, msg='Test negative T failed: setx'):
            self.parser.parse_line('setx -10;', 1)

    def test_nop(self):
        expected = ('0' * 32)
        actual = str(self.parser.parse_line('nop', 1))
        self.assertEqual(expected, actual, 'nop failed')

    def test_comment_filter(self):
        expected = ['sub $0, $0, $0', 'addi $1, $0, 1 # the value is 1']
        actual = self.parser.preprocess_assembly(['sub $0, $0, $0\n', '#hi\n', '\t#hello\n',
                                                  'addi $1, $0, 1 # the value is 1\n'])
        self.assertEqual(expected, actual, 'Comment filter error')

    def test_whitespace_filter(self):
        expected = ['sub $0, $0, $0', 'addi $1, $0, 1']
        actual = self.parser.preprocess_assembly([' sub $0, $0, $0\n', '\n', '\t\n', '\taddi $1, $0, 1\n'])
        self.assertEqual(expected, actual, 'Whitespace filter error')

    def test_target_only_filter(self):
        expected = ['sub $0, $0, $0', 'addi $1, $0, 1']
        actual = self.parser.preprocess_assembly(['sub $0, $0, $0\n', 'loop:\n', '\ttarget:\n', 'addi $1, $0, 1\n'])
        self.assertEqual(expected, actual, 'Target filter error')

    def test_target_inline(self):
        expected = ['sub $0, $0, $0', 'addi $1, $0, 1']
        actual = self.parser.preprocess_assembly(['loop:\tsub $0, $0, $0\n', '\ttarget: addi $1, $0, 1\n'])
        self.assertEqual(expected, actual, 'Inline target filter error')

    def test_branch_target_replacement(self):
        with open('./assembler/test/dat/branch_test.s', 'r') as mips, \
                open('./assembler/test/dat/branch_test.mif', 'r') as mif:
            text = self.parser.preprocess_assembly(mips.readlines())
            actual = [str(self.parser.parse_line(x, i)) for i, x in enumerate(text)]
            # Read in the expected file, remove blank lines (filter), and remove the newline character (map)
            expected = list(map(lambda y: y[:-1], filter(lambda x: not re.match('\s*$', x), mif.readlines())))
            self.assertEqual(actual, expected, 'Error in branch replacement')

    def test_jump_target_replacement(self):
        with open('./assembler/test/dat/jump_test.s', 'r') as mips, open('./assembler/test/dat/jump_test.mif', 'r') as mif:
            text = self.parser.preprocess_assembly(mips.readlines())
            actual = [str(self.parser.parse_line(x, i)) for i, x in enumerate(text)]
            expected = list(map(lambda y: y[:-1], filter(lambda x: not re.match('\s*$', x), mif.readlines())))
            self.assertEqual(actual, expected, 'Error in branch replacement')

    def test_register_replacement(self):
        with open('./assembler/test/dat/reg_replace_test.s', 'r') as mips, \
                open('./assembler/test/dat/reg_replace_test.mif', 'r') as mif:
            text = self.parser.preprocess_assembly(mips.readlines())
            actual = [str(self.parser.parse_line(x, i)) for i, x in enumerate(text)]
            expected = list(map(lambda y: y[:-1], filter(lambda x: not re.match('\s*$', x), mif.readlines())))
            self.assertEqual(actual, expected, 'Error in branch replacement')


if __name__ == '__main__':
    unittest.main()
