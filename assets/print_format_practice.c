#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>


/*
SAVE AS print_format_practice.c
    
gcc -o practice print_format_practice.c && ./practice && rm practice

The Formula
%[flags][width][.precision]type

Cheatsheet
Code	    Value	    Output	Explanation
%d         	5   	    "5"     Normal
%02d	    5	        "05"	Zero pad to size 2
%2d         5   	    " 5"    Space pad to size 2
%-5d	    5	        "5      "	Left align in size 5
%+d	        5   	    "+5"    Force sign
%.2f	    3.149	    "3.15"	2 Decimals (Rounded)
%.3s	    "Hello"	    "Hel"	Truncate string to 3 chars
%#x         255         "0xff"	Hex with prefix
%zu         sizeof(x)   "8"	    Correct size_t type
*/

/* =========================================================================
 * HELPER FUNCTION (Do not edit)
 * ========================================================================= */
void verify(const char *buffer, const char *expected, int test_id, const char *desc) {
    if (strcmp(buffer, expected) != 0) {
        fprintf(stderr, "❌ Test %02d FAILED (%s)\n", test_id, desc);
        fprintf(stderr, "   Expected: [%s]\n", expected);
        fprintf(stderr, "   Got:      [%s]\n", buffer);
        fprintf(stderr, "   Length:   Exp=%zu, Got=%zu\n", strlen(expected), strlen(buffer));
        exit(1);
    }
    printf("✅ Test %02d passed: %s\n", test_id, desc);
}

/* =========================================================================
 * PRACTICE AREA
 * Replace the "__" strings in snprintf with the correct format specifiers.
 * ========================================================================= */
int main(void) {
    char buf[128];

    // --- Integers ---

    // 1. Basic Integer
    // Goal: "123"
    snprintf(buf, sizeof(buf), "__", 123);
    verify(buf, "123", 1, "Basic Integer");

    // 2. Zero Padding (2 digits) - Useful for Days/Months
    // Goal: "05"
    snprintf(buf, sizeof(buf), "__", 5);
    verify(buf, "05", 2, "Zero Pad 2");

    // 3. Zero Padding (4 digits) - Useful for Years or IDs
    // Goal: "0042"
    snprintf(buf, sizeof(buf), "__", 42);
    verify(buf, "0042", 3, "Zero Pad 4");

    // 4. Space Padding (Right align, width 5)
    // Goal: "   99"
    snprintf(buf, sizeof(buf), "__", 99);
    verify(buf, "   99", 4, "Right Align Width 5");

    // 5. Left Align (Width 5)
    // Goal: "99   "
    snprintf(buf, sizeof(buf), "__", 99);
    verify(buf, "99   ", 5, "Left Align Width 5");

    // 6. Explicit Sign (Positive)
    // Goal: "+42"
    snprintf(buf, sizeof(buf), "__", 42);
    verify(buf, "+42", 6, "Force Sign");

    // --- Hexadecimal (System / Network) ---

    // 7. Hex Lowercase
    // Goal: "ff"
    snprintf(buf, sizeof(buf), "__", 255);
    verify(buf, "ff", 7, "Hex Lower");

    // 8. Hex Uppercase
    // Goal: "1A"
    snprintf(buf, sizeof(buf), "__", 26);
    verify(buf, "1A", 8, "Hex Upper");

    // 9. Hex with 0x prefix (Alternate form)
    // Goal: "0xff"
    snprintf(buf, sizeof(buf), "__", 255);
    verify(buf, "0xff", 9, "Hex Alternate");

    // 10. Hex Zero Padded (Standard for MAC addresses/Registers)
    // Goal: "0a"
    snprintf(buf, sizeof(buf), "__", 10);
    verify(buf, "0a", 10, "Hex Zero Pad");

    // --- Strings ---

    // 11. Basic String
    // Goal: "Hello"
    snprintf(buf, sizeof(buf), "__");
    verify(buf, "Hello", 11, "Basic String");

    // 12. String Truncation (First 3 chars)
    // Goal: "Hel"
    snprintf(buf, sizeof(buf), "__");
    verify(buf, "Hel", 12, "Truncate String");

    // 13. String with Padding (Right align)
    // Goal: "   Hi"
    snprintf(buf, sizeof(buf), "__");
    verify(buf, "   Hi", 13, "String Padding");

    // --- Floating Point ---

    // 14. Float (2 decimal places) - Standard for money/stats
    // Goal: "3.14"
    snprintf(buf, sizeof(buf), "__", 3.14159);
    verify(buf, "3.14", 14, "Float Precision 2");

    // 15. Float (No decimal digits, rounded)
    // Goal: "4"
    snprintf(buf, sizeof(buf), "__", 3.9);
    verify(buf, "4", 15, "Float Round No Decimals");

    // --- System Types (Important for portability) ---

    // 16. size_t (Unsigned) - returned by sizeof(), strlen()
    // Goal: "100"
    size_t size = 100;
    snprintf(buf, sizeof(buf), "__", size);
    verify(buf, "100", 16, "size_t");

    // 17. long long (64-bit signed)
    // Goal: "123456789"
    long long big_num = 123456789;
    snprintf(buf, sizeof(buf), "__", big_num);
    verify(buf, "123456789", 17, "long long");

    // --- Advanced / Combo ---

    // 18. Dynamic Width (Using *)
    // Goal: "  Hi" (Width is passed as argument 4)
    snprintf(buf, sizeof(buf), "__");
    verify(buf, "  Hi", 18, "Dynamic Width");

    // 19. IP Address Octet Style (Zero pad to 3)
    // Goal: "001"
    snprintf(buf, sizeof(buf), "__", 1);
    verify(buf, "001", 19, "IP Octet Style");

    // 20. Literal Percent Sign
    // Goal: "50%"
    snprintf(buf, sizeof(buf), "__", 50);
    verify(buf, "50%", 20, "Literal Percent");

    printf("\n🎉 CONGRATULATIONS! ALL TESTS PASSED.\n");
    return 0;
}





































/* 




1. The "Flags" (The padding and alignment tricks)

These go immediately after the %.

    0 (Zero Padding) -> What you were looking for.
    Fills the empty space with zeros instead of spaces.

        %02d -> prints 1 as "01", 10 as "10".

        %04d -> prints 5 as "0005".

        Use case: Time (12:05), Dates (2023-01-01), ID numbers.

    - (Left Align)
    By default, numbers align to the right (like in Excel). This forces them to the left.

        %-5d -> prints 1 as "1 " (spaces on right).

        Use case: Printing columns of text or tables.

    + (Force Sign)
    Forces a + sign for positive numbers (normally only - is shown).

        %+d -> prints 5 as "+5", -5 as "-5".

    # (Alternate Form)
    Mostly used with Hex to add the 0x prefix automatically.

        %#x -> prints 255 as "0xff".






 * =========================================================================
 * SPOILER: CHEAT SHEET (Scroll down only if stuck)
 * =========================================================================
 *
 *
 *
 *
 *
 *
 *
 *
 *
 * 1.  "%d"
 * 2.  "%02d"
 * 3.  "%04d"
 * 4.  "%5d"
 * 5.  "%-5d"
 * 6.  "%+d"
 * 7.  "%x"
 * 8.  "%X"
 * 9.  "%#x"
 * 10. "%02x"
 * 11. "%s"
 * 12. "%.3s"
 * 13. "%5s"
 * 14. "%.2f"
 * 15. "%.0f"
 * 16. "%zu"  (z is for size_t)
 * 17. "%lld" (ll is for long long)
 * 18. "%*s"
 * 19. "%03d"
 * 20. "%d%%"
 */