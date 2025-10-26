from pathlib import Path
from fastapi_code_generator.__main__ import generate_code
from datamodel_code_generator import DataModelType, PythonVersion

def main():
    # Define paths
    repo_dir = Path(__file__).resolve().parent.parent.parent
    target_dir = repo_dir / 'src/api/stubs/event'
    input_file = repo_dir / 'src/api/specifications/event.yaml'
    template_dir = repo_dir / 'src/api/templates/event'

    # Ensure output directory exists
    target_dir.mkdir(parents=True, exist_ok=True)

    # Read input file
    with input_file.open(encoding="utf-8") as f:
        input_text = f.read()

    # Generate the FastAPI code
    generate_code(
        input_name=str(input_file),
        input_text=input_text,
        encoding="utf-8",
        output_dir=target_dir,
        template_dir=template_dir,
        model_template_dir=None,
        model_path=None,
        custom_visitors=None,
        disable_timestamp=False,
        generate_routers=True,
        specify_tags=None,
        output_model_type=DataModelType.PydanticV2BaseModel,
        python_version=PythonVersion.PY_311,
    )

if __name__ == "__main__":
    main()