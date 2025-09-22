#!/usr/bin/env python3
"""
Expression Set Checker - Multilingual Mathematical Analysis Tool
================================================================

This program analyzes mathematical expressions and constants to determine:
- Set membership (N or N*)
- Even/Odd patterns (2*K vs 2*K+1)
- Prime number analysis
- Complete mathematical analysis

Supports English, French, and Arabic languages.

Requirements:
- sympy (pip install sympy)
- translations.json file in the same directory

Author: Thepoff1327
Version: 2.0
"""

import sympy as sp
from sympy import symbols, sympify, simplify, expand, factor, isprime
import re
import math
import json
import os
import sys

def load_translations():
    """Load translations from JSON file"""
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'translations.json')
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: translations.json file not found!")
        print("Please make sure translations.json is in the same directory as this script.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error reading translations.json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error loading translations: {e}")
        sys.exit(1)

def get_text(key, lang='en', texts=None):
    """Get text in specified language"""
    if texts is None:
        return key  # Fallback if texts not loaded
    return texts[lang].get(key, texts['en'].get(key, key))

def choose_language(texts):
    """Let user choose language"""
    print(get_text('choose_language', 'en', texts))
    while True:
        try:
            choice = input("Enter choice (1/2/3): ").strip()
            if choice == '1':
                return 'en'
            elif choice == '2':
                return 'fr'
            elif choice == '3':
                return 'ar'
            else:
                print(get_text('invalid_choice', 'en', texts))
        except KeyboardInterrupt:
            print(f"\n\n{get_text('interrupted', 'en', texts)}")
            sys.exit(0)
        except Exception:
            print(get_text('invalid_choice', 'en', texts))

def analyze_constant(value, set_choice, lang, texts):
    """Analyze a constant value (no 'n' variable)"""
    
    print(f"\n{get_text('constant_analysis', lang, texts)}")
    print("-" * 30)
    
    print(get_text('constant_value', lang, texts).format(value))
    
    # Check set membership
    print(f"\n{get_text('set_membership', lang, texts)}")
    
    if set_choice == 'N':
        belongs = value >= 0 and (isinstance(value, int) or value == int(value))
        set_status = get_text('belongs_to_n', lang, texts) if belongs else get_text('not_belongs_to_n', lang, texts)
    else:  # N*
        belongs = value > 0 and (isinstance(value, int) or value == int(value))
        set_status = get_text('belongs_to_n_star', lang, texts) if belongs else get_text('not_belongs_to_n_star', lang, texts)
    
    print(f"{get_text('constant_evaluation', lang, texts)}")
    print(f"  {value} {set_status}")
    
    # Parity and prime analysis for integers
    if isinstance(value, (int, float)) and value == int(value):
        value_int = int(value)
        
        # Parity analysis
        print(f"\n{get_text('parity_analysis', lang, texts)}")
        print("-" * 40)
        
        if value_int % 2 == 0:
            k_val = value_int // 2
            print(f"  {value_int} = {get_text('even', lang, texts)}, K = {k_val}")
        else:
            k_val = (value_int - 1) // 2
            print(f"  {value_int} = {get_text('odd', lang, texts)}, K = {k_val}")
        
        # Prime analysis
        if value_int > 1:
            is_prime = isprime(value_int)
            if is_prime:
                print(f"  └─ {get_text('prime', lang, texts).format(value_int)}")
                print(f"     {get_text('prime_divisors', lang, texts).format(value_int)}")
            else:
                divisors = get_divisors(value_int)
                print(f"  └─ {get_text('composite', lang, texts).format(value_int)}")
                print(f"     {get_text('all_divisors', lang, texts).format(sorted(divisors))}")
        elif value_int == 1:
            print(f"  └─ {get_text('neither_prime', lang, texts)}")
            print(f"     {get_text('divisors_one', lang, texts)}")
        elif value_int == 0:
            print(f"  └─ 🔢 0 has special properties (not prime, not composite)")
        else:
            print(f"  └─ {get_text('prime_na', lang, texts)}")
    else:
        print(f"\n{get_text('parity_analysis', lang, texts)}")
        print("-" * 40)
        print(f"  {value} {get_text('non_integer', lang, texts)}")
        print(f"  {get_text('prime_na_non_integer', lang, texts)}")

def analyze_expression(expr, set_choice, n, lang, texts):
    """Analyze the expression symbolically"""
    
    print(f"\n{get_text('symbolic_analysis', lang, texts)}")
    print("-" * 30)
    
    # Expand and simplify the expression
    expanded = expand(expr)
    simplified = simplify(expr)
    
    print(get_text('original', lang, texts).format(expr))
    print(get_text('expanded', lang, texts).format(expanded))
    print(get_text('simplified', lang, texts).format(simplified))
    
    # Check if expression is always positive for valid n values
    print(f"\n{get_text('set_membership', lang, texts)}")
    
    min_n = 1 if set_choice == 'N*' else 0
    
    # Test a few values to get insight
    test_vals = []
    problematic_vals = []
    
    for test_n in range(min_n, min_n + 10):
        try:
            result = float(expr.subs(n, test_n))
            test_vals.append((test_n, result))
            
            # Check if result belongs to the chosen set
            if set_choice == 'N' and result < 0:
                problematic_vals.append((test_n, result))
            elif set_choice == 'N*' and result <= 0:
                problematic_vals.append((test_n, result))
                
        except Exception as e:
            print(get_text('could_not_evaluate', lang, texts).format(test_n, e))
    
    # Display results for test values
    print(f"\n{get_text('sample_evaluations', lang, texts)}")
    for test_n, result in test_vals[:5]:
        belongs = "✅" if ((set_choice == 'N' and result >= 0) or (set_choice == 'N*' and result > 0)) else "❌"
        print(f"  n = {test_n}: {expr} = {result} {belongs}")
    
    if problematic_vals:
        print(f"\n{get_text('found_problems', lang, texts).format(set_choice)}")
        for test_n, result in problematic_vals:
            print(f"  n = {test_n}: result = {result}")
    else:
        print(f"\n{get_text('appears_to_belong', lang, texts).format(set_choice)}")
    
    # Even/Odd analysis
    analyze_parity(expr, n, min_n, lang, texts)

def analyze_parity(expr, n, min_n, lang, texts):
    """Analyze if the expression results in even (2*K) or odd (2*K+1) numbers"""
    
    print(f"\n{get_text('parity_analysis', lang, texts)}")
    print("-" * 40)
    
    # Check parity for several values
    even_count = 0
    odd_count = 0
    parity_pattern = []
    
    for test_n in range(min_n, min_n + 10):
        try:
            result = float(expr.subs(n, test_n))
            if result == int(result):
                result = int(result)
            
            is_even = int(result) % 2 == 0 if result == int(result) else None
            parity_pattern.append(is_even)
            
            if is_even is not None:
                if is_even:
                    even_count += 1
                    parity_type = get_text('even', lang, texts)
                    k_value = int(result) // 2
                else:
                    odd_count += 1
                    parity_type = get_text('odd', lang, texts)
                    k_value = (int(result) - 1) // 2
                
                print(f"  n = {test_n}: {result} = {parity_type}, K = {k_value}")
                
                # Add prime checking for integer results
                if int(result) > 1 and int(result) <= 1000:
                    if isprime(int(result)):
                        print(f"    └─ {get_text('prime', lang, texts).format(result)}")
                    else:
                        print(f"    └─ {get_text('composite', lang, texts).format(result)}")
            else:
                print(f"  n = {test_n}: {result} {get_text('non_integer', lang, texts)}")
                
        except Exception as e:
            print(f"  n = {test_n}: Error - {e}")
    
    # Analyze pattern
    print(f"\n{get_text('pattern_summary', lang, texts)}")
    if even_count > 0 and odd_count > 0:
        print(get_text('produces_both', lang, texts))
    elif even_count > 0:
        print(get_text('produces_even', lang, texts))
    elif odd_count > 0:
        print(get_text('produces_odd', lang, texts))
    else:
        print(get_text('pattern_unclear', lang, texts))
    
    # Try to determine parity symbolically
    try:
        # Check if expression mod 2 gives consistent results
        mod_expr = expr % 2
        simplified_mod = simplify(mod_expr)
        print(f"{get_text('mod_expression', lang, texts).format(simplified_mod)}")
        
        if simplified_mod == 0:
            print(get_text('always_even', lang, texts))
        elif simplified_mod == 1:
            print(get_text('always_odd', lang, texts))
        else:
            print(get_text('depends_on_n', lang, texts))
            
    except Exception as e:
        print(get_text('could_not_determine', lang, texts).format(e))

def test_specific_values(expr, set_choice, n, lang, texts):
    """Allow user to test specific values of n"""
    
    print(f"\n{get_text('specific_testing', lang, texts)}")
    print("-" * 30)
    
    min_n = 1 if set_choice == 'N*' else 0
    print(get_text('note_range', lang, texts).format(set_choice, min_n))
    
    done_words = {'en': 'done', 'fr': 'fini', 'ar': 'انتهى'}
    
    while True:
        try:
            n_input = input(f"\n{get_text('enter_n_value', lang, texts)}").strip()
            
            if n_input.lower() == done_words[lang]:
                break
            
            n_value = float(n_input)
            
            # Check if n is valid for the chosen set
            if set_choice == 'N*' and n_value < 1:
                print(get_text('warning_not_in_set', lang, texts).format(n_value, set_choice, 1))
            elif set_choice == 'N' and n_value < 0:
                print(get_text('warning_not_in_set', lang, texts).format(n_value, set_choice, 0))
            
            # Evaluate expression
            result = float(expr.subs(n, n_value))
            if result == int(result):
                result = int(result)
            
            print(f"\n{get_text('result_for_n', lang, texts).format(n_value)}")
            print(f"   {expr} = {result}")
            
            # Check set membership
            if set_choice == 'N':
                belongs = result >= 0 and (isinstance(result, int) or result == int(result))
                set_status = get_text('belongs_to_n', lang, texts) if belongs else get_text('not_belongs_to_n', lang, texts)
            else:  # N*
                belongs = result > 0 and (isinstance(result, int) or result == int(result))
                set_status = get_text('belongs_to_n_star', lang, texts) if belongs else get_text('not_belongs_to_n_star', lang, texts)
            
            print(f"   {get_text('set_membership_result', lang, texts).format(set_status)}")
            
            # Check parity if it's an integer
            if isinstance(result, (int, float)) and result == int(result):
                result_int = int(result)
                if result_int % 2 == 0:
                    k_val = result_int // 2
                    print(f"   {get_text('parity_even', lang, texts).format(k_val)}")
                else:
                    k_val = (result_int - 1) // 2
                    print(f"   {get_text('parity_odd', lang, texts).format(k_val)}")
                
                # Check if it's prime
                if result_int > 1:
                    is_prime = isprime(result_int)
                    if is_prime:
                        print(f"   {get_text('prime_analysis', lang, texts).format(result_int)}")
                        print(f"   {get_text('prime_divisors', lang, texts).format(result_int)}")
                    else:
                        # Find divisors for composite numbers
                        divisors = get_divisors(result_int)
                        print(f"   {get_text('composite_analysis', lang, texts).format(result_int)}")
                        print(f"   {get_text('all_divisors', lang, texts).format(sorted(divisors))}")
                elif result_int == 1:
                    print(f"   {get_text('neither_prime', lang, texts)}")
                    print(f"   {get_text('divisors_one', lang, texts)}")
                else:
                    print(f"   {get_text('prime_na', lang, texts)}")
            else:
                print(f"   {get_text('parity_na', lang, texts)}")
                print(f"   {get_text('prime_na_non_integer', lang, texts)}")
                
        except ValueError:
            print(get_text('enter_valid_number', lang, texts))
        except Exception as e:
            print(get_text('error_evaluating', lang, texts).format(e))

def get_divisors(n):
    """Get all divisors of a positive integer n"""
    if n <= 0:
        return []
    
    divisors = []
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divisors.append(i)
            if i != n // i:  # Avoid adding the same divisor twice for perfect squares
                divisors.append(n // i)
    return divisors

def main():
    """Main program function"""
    # Load translations
    texts = load_translations()
    
    # Choose language first
    lang = choose_language(texts)
    
    print("\n" + get_text('welcome', lang, texts))
    print("=" * 50)
    print(get_text('description', lang, texts) + "\n")
    
    # Step 1: Ask for N or N*
    while True:
        set_choice = input(get_text('choose_set', lang, texts)).strip().upper()
        if set_choice in ['N', 'N*']:
            break
        print(get_text('invalid_set', lang, texts))
    
    if set_choice == 'N':
        print(f"\n{get_text('chose_n', lang, texts)}")
        print(get_text('n_description', lang, texts))
        valid_range = "n ≥ 0"
    else:
        print(f"\n{get_text('chose_n_star', lang, texts)}")
        print(get_text('n_star_description', lang, texts))
        valid_range = "n ≥ 1"
    
    # Step 2: Get the expression
    while True:
        try:
            expression_input = input(f"\n{get_text('enter_expression', lang, texts)}").strip()
            
            # Clean up the input - replace implicit multiplication and handle division
            expression_input = expression_input.replace('n(', 'n*(')
            expression_input = expression_input.replace(')n', ')*n')
            # Handle cases like 25n -> 25*n
            expression_input = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression_input)
            expression_input = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expression_input)
            
            # Parse the expression
            n = symbols('n')
            expr = sympify(expression_input)
            
            # Check if 'n' is in the expression
            has_n = expr.has(n)
            if not has_n:
                print(get_text('no_n_variable', lang, texts))
                # For constants, we'll analyze the single value
                constant_value = float(expr)
                if constant_value == int(constant_value):
                    constant_value = int(constant_value)
                analyze_constant(constant_value, set_choice, lang, texts)
                print(f"\n{get_text('analysis_complete', lang, texts)}")
                return
                
            break
            
        except Exception as e:
            print(get_text('invalid_expression', lang, texts).format(str(e)))
            print(get_text('multiplication_tip', lang, texts))
    
    print(f"\n{get_text('expression_parsed', lang, texts).format(expr)}")
    
    # Use fallback for analyzing text if not in translations
    analyzing_text = get_text('analyzing', lang, texts)
    if '{}' in analyzing_text:
        print(analyzing_text.format(valid_range))
    else:
        print(f"📊 Analyzing expression for {valid_range}...")
    
    # Step 3: Symbolic analysis
    analyze_expression(expr, set_choice, n, lang, texts)
    
    # Step 4: Ask for specific n values to test
    print(f"\n{get_text('test_specific', lang, texts)}")
    yes_responses = {'en': 'y', 'fr': 'o', 'ar': 'ن'}
    test_values = input(get_text('yes_no', lang, texts)).strip().lower()
    
    if test_values == yes_responses[lang]:
        test_specific_values(expr, set_choice, n, lang, texts)
    
    print(f"\n{get_text('analysis_complete', lang, texts)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n👋 Program interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please restart the program and try again.")
        sys.exit(1)