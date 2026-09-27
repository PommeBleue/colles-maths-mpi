import re
from pathlib import Path

def merge_tex_files(sections_dir="sections", output_dir="merged_sections"):
    # Setup directories
    src_path = Path(sections_dir)
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)

    # Regex to extract solutions from *corr.tex files
    # Matches \begin{proof} or \begin{solution} and captures the label and the entire block
    solution_pattern = re.compile(
        r"(\\begin\{(?:proof|solution)\}\[Correction de l'exercice \\ref\{([^}]+)\}\].*?\\end\{(?:proof|solution)\})",
        re.DOTALL
    )

    # Regex to locate the exercises in the base .tex files
    # Captures the entire exo block and the label inside it
    exo_pattern = re.compile(
        r"(\\begin\{exo\}.*?\\label\{([^}]+)\}.*?\\end\{exo\})",
        re.DOTALL
    )

    # Find all correction files
    corr_files = list(src_path.glob("*corr.tex"))

    for corr_file in corr_files:
        # Determine the corresponding base exercise file (e.g., alcorr.tex -> al.tex)
        base_name = corr_file.name.replace("corr.tex", ".tex")
        base_file = src_path / base_name

        if not base_file.exists():
            print(f"Skipping {corr_file.name}: Could not find matching base file {base_name}.")
            continue

        # Extract all solutions into a dictionary: { 'label': 'full_latex_solution_string' }
        corr_content = corr_file.read_text(encoding="utf-8")
        solutions = {}
        for match in solution_pattern.finditer(corr_content):
            full_solution_block = match.group(1)
            label = match.group(2)
            solutions[label] = full_solution_block

        # Read the base exercise file
        base_content = base_file.read_text(encoding="utf-8")

        # Function to inject the solution right after the \end{exo}
        def inject_solution(match):
            exo_block = match.group(1)
            label = match.group(2)
            
            if label in solutions:
                # Add a blank line and the solution block right after \end{exo}
                return f"{exo_block}\n\n{solutions[label]}"
            
            # If no matching solution is found, leave the exercise block as is
            return exo_block

        # Apply the replacement
        merged_content = exo_pattern.sub(inject_solution, base_content)

        # Write to the new directory
        output_file = out_path / base_name
        output_file.write_text(merged_content, encoding="utf-8")
        print(f"Successfully merged {len(solutions)} solutions into {output_file.name}")

if __name__ == "__main__":
    merge_tex_files()
