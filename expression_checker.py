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
Enhanced with support for multiple variables (a-z) and square notation (²)

Requirements:
- sympy (pip install sympy)
- translations.json file in the same directory

Author: Thepoff1327
Version: 2.1 (Enhanced)
"""

import sympy as sp
from sympy import symbols, sympify, simplify, expand, factor, isprime
import re
import math
import json
import os
import sys
import string

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

def preprocess_expression(expression_input):
    """
    Enhanced preprocessing to handle multiple variables and square notation
    """
    # Handle square notation (²) 
    expression_input = expression_input.replace('²', '**2')
    
    # Clean up the input - replace implicit multiplication
    # Handle cases like 2n, 3a, 5x -> 2*n, 3*a, 5*x
    expression_input = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expression_input)
    # Handle cases like n2, a3, x5 -> n*2, a*3, x*5
    expression_input = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expression_input)
    
    # Handle parentheses multiplication like n(x+1) -> n*(x+1)
    expression_input = re.sub(r'([a-zA-Z])\(', r'\1*(', expression_input)
    expression_input = re.sub(r'\)([a-zA-Z])', r')*\1', expression_input)
    
    # Handle variable-to-variable multiplication like nx, ab, xy -> n*x, a*b, x*y
    expression_input = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expression_input)
    
    return expression_input

def find_variables(expr):
    """
    Find all variables in the expression
    """
    # Get all free symbols (variables) from the expression
    variables = list(expr.free_symbols)
    # Sort them alphabetically for consistency
    variables.sort(key=str)
    return variables

def get_primary_variable(variables, lang, texts):
    """
    Let user choose which variable to analyze (for multi-variable expressions)
    """
    if len(variables) == 1:
        return variables[0]
    
    print(f"\n🔍 Multiple variables found: {[str(v) for v in variables]}")
    print("Which variable would you like to analyze as the main variable?")
    
    for i, var in enumerate(variables, 1):
        print(f"{i}. {var}")
    
    while True:
        try:
            choice = input(f"Enter choice (1-{len(variables)}): ").strip()
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(variables):
                return variables[choice_idx]
            else:
                print(f"Please enter a number between 1 and {len(variables)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print(f"\n\n{get_text('interrupted', lang, texts)}")
            sys.exit(0)

def get_other_variable_values(variables, primary_var, lang, texts):
    """
    Get fixed values for other variables when analyzing multi-variable expressions
    """
    other_vars = [v for v in variables if v != primary_var]
    if not other_vars:
        return {}
    
    print(f"\n📝 For analysis, we need fixed values for other variables:")
    var_values = {}
    
    for var in other_vars:
        while True:
            try:
                value_input = input(f"Enter value for {var} (or press Enter for {var}=1): ").strip()
                if value_input == "":
                    var_values[var] = 1
                    print(f"   Using {var} = 1")
                    break
                else:
                    value = float(value_input)
                    if value == int(value):
                        value = int(value)
                    var_values[var] = value
                    print(f"   Using {var} = {value}")
                    break
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print(f"\n\n{get_text('interrupted', lang, texts)}")
                sys.exit(0)
    
    return var_values

def analyze_constant(value, set_choice, lang, texts):
    """Analyze a constant value (no variables)"""
    
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

def analyze_expression(expr, set_choice, primary_var, var_values, lang, texts):
    """Analyze the expression symbolically with support for multiple variables"""
    
    print(f"\n{get_text('symbolic_analysis', lang, texts)}")
    print("-" * 30)
    
    # Substitute fixed values for other variables
    working_expr = expr
    if var_values:
        print(f"🔧 Substituting fixed values: {var_values}")
        working_expr = expr.subs(var_values)
        print(f"Expression with substitutions: {working_expr}")
    
    # Expand and simplify the expression
    expanded = expand(working_expr)
    simplified = simplify(working_expr)
    
    print(get_text('original', lang, texts).format(working_expr))
    print(get_text('expanded', lang, texts).format(expanded))
    print(get_text('simplified', lang, texts).format(simplified))
    
    # Check if expression is always positive for valid primary variable values
    print(f"\n{get_text('set_membership', lang, texts)}")
    
    min_val = 1 if set_choice == 'N*' else 0
    
    # Test a few values to get insight
    test_vals = []
    problematic_vals = []
    
    for test_val in range(min_val, min_val + 10):
        try:
            result = float(working_expr.subs(primary_var, test_val))
            test_vals.append((test_val, result))
            
            # Check if result belongs to the chosen set
            if set_choice == 'N' and result < 0:
                problematic_vals.append((test_val, result))
            elif set_choice == 'N*' and result <= 0:
                problematic_vals.append((test_val, result))
                
        except Exception as e:
            print(get_text('could_not_evaluate', lang, texts).format(test_val, e))
    
    # Display results for test values
    print(f"\n{get_text('sample_evaluations', lang, texts)}")
    for test_val, result in test_vals[:5]:
        belongs = "✅" if ((set_choice == 'N' and result >= 0) or (set_choice == 'N*' and result > 0)) else "❌"
        print(f"  {primary_var} = {test_val}: {working_expr} = {result} {belongs}")
    
    if problematic_vals:
        print(f"\n{get_text('found_problems', lang, texts).format(set_choice)}")
        for test_val, result in problematic_vals:
            print(f"  {primary_var} = {test_val}: result = {result}")
    else:
        print(f"\n{get_text('appears_to_belong', lang, texts).format(set_choice)}")
    
    # Even/Odd analysis
    analyze_parity(working_expr, primary_var, min_val, lang, texts)

def analyze_parity(expr, primary_var, min_val, lang, texts):
    """Analyze if the expression results in even (2*K) or odd (2*K+1) numbers"""
    
    print(f"\n{get_text('parity_analysis', lang, texts)}")
    print("-" * 40)
    
    # Check parity for several values
    even_count = 0
    odd_count = 0
    parity_pattern = []
    
    for test_val in range(min_val, min_val + 10):
        try:
            result = float(expr.subs(primary_var, test_val))
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
                
                print(f"  {primary_var} = {test_val}: {result} = {parity_type}, K = {k_value}")
                
                # Add prime checking for integer results
                if int(result) > 1 and int(result) <= 1000:
                    if isprime(int(result)):
                        print(f"    └─ {get_text('prime', lang, texts).format(result)}")
                    else:
                        print(f"    └─ {get_text('composite', lang, texts).format(result)}")
            else:
                print(f"  {primary_var} = {test_val}: {result} {get_text('non_integer', lang, texts)}")
                
        except Exception as e:
            print(f"  {primary_var} = {test_val}: Error - {e}")
    
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

def test_specific_values(expr, set_choice, primary_var, var_values, lang, texts):
    """Allow user to test specific values of the primary variable"""
    
    print(f"\n{get_text('specific_testing', lang, texts)}")
    print("-" * 30)
    
    min_val = 1 if set_choice == 'N*' else 0
    print(f"📝 Testing values for variable '{primary_var}' (range: {primary_var} ≥ {min_val})")
    
    if var_values:
        print(f"🔧 Other variables fixed at: {var_values}")
    
    done_words = {'en': 'done', 'fr': 'fini', 'ar': 'انتهى'}
    
    while True:
        try:
            val_input = input(f"\nEnter value for {primary_var} (or '{done_words[lang]}' to finish): ").strip()
            
            if val_input.lower() == done_words[lang]:
                break
            
            val_value = float(val_input)
            
            # Check if value is valid for the chosen set
            if set_choice == 'N*' and val_value < 1:
                print(f"⚠️  Warning: {val_value} is not in {set_choice} (requires ≥ 1)")
            elif set_choice == 'N' and val_value < 0:
                print(f"⚠️  Warning: {val_value} is not in {set_choice} (requires ≥ 0)")
            
            # Create substitution dictionary
            subs_dict = var_values.copy() if var_values else {}
            subs_dict[primary_var] = val_value
            
            # Evaluate expression
            result = float(expr.subs(subs_dict))
            if result == int(result):
                result = int(result)
            
            print(f"\n📊 Result for {primary_var} = {val_value}:")
            print(f"   {expr} = {result}")
            
            # Check set membership
            if set_choice == 'N':
                belongs = result >= 0 and (isinstance(result, int) or result == int(result))
                set_status = get_text('belongs_to_n', lang, texts) if belongs else get_text('not_belongs_to_n', lang, texts)
            else:  # N*
                belongs = result > 0 and (isinstance(result, int) or result == int(result))
                set_status = get_text('belongs_to_n_star', lang, texts) if belongs else get_text('not_belongs_to_n_star', lang, texts)
            
            print(f"   Set membership: {set_status}")
            
            # Check parity if it's an integer
            if isinstance(result, (int, float)) and result == int(result):
                result_int = int(result)
                if result_int % 2 == 0:
                    k_val = result_int // 2
                    print(f"   Parity: Even (2×{k_val})")
                else:
                    k_val = (result_int - 1) // 2
                    print(f"   Parity: Odd (2×{k_val}+1)")
                
                # Check if it's prime
                if result_int > 1:
                    is_prime = isprime(result_int)
                    if is_prime:
                        print(f"   Prime Analysis: {result_int} is PRIME")
                        print(f"   Divisors: 1, {result_int}")
                    else:
                        # Find divisors for composite numbers
                        divisors = get_divisors(result_int)
                        print(f"   Prime Analysis: {result_int} is COMPOSITE")
                        print(f"   All divisors: {sorted(divisors)}")
                elif result_int == 1:
                    print(f"   Prime Analysis: 1 is neither prime nor composite")
                    print(f"   Divisors: 1")
                else:
                    print(f"   Prime Analysis: Not applicable for {result_int}")
            else:
                print(f"   Parity: Not applicable (non-integer)")
                print(f"   Prime Analysis: Not applicable (non-integer)")
                
        except ValueError:
            print("Please enter a valid number")
        except Exception as e:
            print(f"Error evaluating expression: {e}")

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
    print(get_text('description', lang, texts))
    print("✨ Enhanced with support for multiple variables (a-z) and square notation (²)")
    print()
    
    # Step 1: Ask for N or N*
    while True:
        set_choice = input(get_text('choose_set', lang, texts)).strip().upper()
        if set_choice in ['N', 'N*']:
            break
        print(get_text('invalid_set', lang, texts))
    
    if set_choice == 'N':
        print(f"\n{get_text('chose_n', lang, texts)}")
        print(get_text('n_description', lang, texts))
        valid_range_template = "variable ≥ 0"
    else:
        print(f"\n{get_text('chose_n_star', lang, texts)}")
        print(get_text('n_star_description', lang, texts))
        valid_range_template = "variable ≥ 1"
    
    # Step 2: Get the expression
    while True:
        try:
            print("\n📝 Expression Input Tips:")
            print("  • Use any letters a-z as variables (e.g., 2x + 3y)")
            print("  • Use ² for squares (e.g., x² + 2x)")
            print("  • Multiplication: 2n, 3x, ab (automatically handled)")
            print("  • Examples: n², 2x+1, a²+b², (x+1)²")
            
            expression_input = input(f"\n{get_text('enter_expression', lang, texts)}").strip()
            
            # Enhanced preprocessing for multiple variables and squares
            processed_input = preprocess_expression(expression_input)
            print(f"🔧 Processed: {expression_input} → {processed_input}")
            
            # Parse the expression
            expr = sympify(processed_input)
            
            # Find all variables in the expression
            variables = find_variables(expr)
            
            if not variables:
                print("🔢 No variables found - analyzing as constant")
                # For constants, we'll analyze the single value
                constant_value = float(expr)
                if constant_value == int(constant_value):
                    constant_value = int(constant_value)
                analyze_constant(constant_value, set_choice, lang, texts)
                print(f"\n{get_text('analysis_complete', lang, texts)}")
                return
            
            # Choose primary variable for analysis
            primary_var = get_primary_variable(variables, lang, texts)
            
            # Get values for other variables if any
            var_values = get_other_variable_values(variables, primary_var, lang, texts)
            
            break
            
        except Exception as e:
            print(f"❌ Invalid expression: {str(e)}")
            print("💡 Make sure to use proper mathematical notation")
    
    print(f"\n✅ Expression parsed successfully: {expr}")
    print(f"📊 Primary variable for analysis: {primary_var}")
    if var_values:
        print(f"🔧 Fixed values: {var_values}")
    
    valid_range = valid_range_template.replace("variable", str(primary_var))
    print(f"📈 Analyzing for {valid_range}...")
    
    # Step 3: Symbolic analysis
    analyze_expression(expr, set_choice, primary_var, var_values, lang, texts)
    
    # Step 4: Ask for specific values to test
    print(f"\n🧪 Would you like to test specific values for {primary_var}?")
    yes_responses = {'en': 'y', 'fr': 'o', 'ar': 'ن'}
    test_values = input(get_text('yes_no', lang, texts)).strip().lower()
    
    if test_values == yes_responses[lang]:
        test_specific_values(expr, set_choice, primary_var, var_values, lang, texts)
    
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