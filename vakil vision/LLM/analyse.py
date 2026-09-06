from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from LLM.factory import get_llm
from Models.PydanticContract import ContractAnalysis, ContractAnalysisBase

parser = PydanticOutputParser(pydantic_object=ContractAnalysisBase)

prompt = ChatPromptTemplate.from_template(
    "Analyse the following contract and extract the required information.\n\n"
    "Contract:\n{contract}\n\n"
    "{format_instructions}"
)


def analyse_contract(contract: str, model: str | None = None) -> ContractAnalysis:
    """Run structured contract analysis using the configured or selected model."""
    llm = get_llm(model=model)
    chain = prompt | llm | parser
    result: ContractAnalysisBase = chain.invoke(
        {
            "contract": contract,
            "format_instructions": parser.get_format_instructions(),
        }
    )
    return ContractAnalysis(**result.model_dump())


def chat_with_model(message: str, context: str, model: str | None = None) -> str:
    """Free-form chat using the reasoning model."""
    llm = get_llm(model=model)
    response = llm.invoke(
        f"Context:\n{context}\n\nUser message:\n{message}\n\n"
        "Reply clearly and concisely."
    )
    return str(response.content)
