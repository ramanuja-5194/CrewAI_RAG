from crewai import Agent, Crew, Process, Task
from crewai_tools import PDFSearchTool
from dotenv import load_dotenv

load_dotenv()

# --- Tools ---
# PDF SOURCE: https://www.gpinspect.com/wp-content/uploads/2021/03/sample-home-report-inspection.pdf
pdf_search_tool = PDFSearchTool(
    pdf="./example_home_inspection.pdf",
    # Optionally, configure the PDFSearchTool to use the Gemini LLM for embeddings/summarization
    # By default, it might try to use OpenAI or its own default.
    # do not put OPENAI_API_KEY=NA when using this.
    config=dict(
        llm=dict(
            provider="google",
            config=dict(
                model="gemini-2.5-flash",
                temperature=0.7,
            ),
        ),
        embedder=dict(
            provider="google",
            config=dict(
                model="models/embedding-001", # Standard Gemini embedding model
                task_type="retrieval_document",
            ),
        ),
    )
)

# --- Agents ---
research_agent = Agent(
    role="Research Agent",
    goal="Search through the PDF to find relevant answers",
    allow_delegation=False,
    verbose=True,
    backstory=(
        """
        The research agent is adept at searching and 
        extracting data from documents, ensuring accurate and prompt responses.
        """
    ),
    tools=[pdf_search_tool],
    llm="gemini/gemini-2.5-flash",

)

professional_writer_agent = Agent(
    role="Professional Writer",
    goal="Write professional emails based on the research agent's findings",
    allow_delegation=False,
    verbose=True,
    backstory=(
        """
        The professional writer agent has excellent writing skills and is able to craft 
        clear and concise emails based on the provided information.
        """
    ),
    tools=[],
    llm="gemini/gemini-2.5-flash",
)


# --- Tasks ---
answer_customer_question_task = Task(
    description=(
        """
        Answer the customer's questions based on the home inspection PDF.
        The research agent will search through the PDF to find the relevant answers.
        Your final answer MUST be clear and accurate, based on the content of the home
        inspection PDF.

        Here is the customer's question:
        {customer_question}
        """
    ),
    expected_output="""
        Provide clear and accurate answers to the customer's questions based on 
        the content of the home inspection PDF.
        """,
    tools=[pdf_search_tool],
    agent=research_agent,
)

write_email_task = Task(
    description=(
        """
        - Write a professional email to a contractor based 
          on the research agent's findings.
        - The email should clearly state the issues found in the specified section 
          of the report and request a quote or action plan for fixing these issues.
        - Ensure the email is signed with the following details:

          Best regards,

          L A V Ramanuja.
        """
    ),
    expected_output="""
        Write a clear and concise email that can be sent to a contractor to address the 
        issues found in the home inspection report.
        """,
    tools=[],
    agent=professional_writer_agent,
)

# --- Crew ---
crew = Crew(
    agents=[research_agent, professional_writer_agent],
    tasks=[answer_customer_question_task, write_email_task],
    process=Process.sequential,
    # You can also set a default LLM for the entire crew if you don't
    # want to specify it for each agent individually:
    # llm="gemini/gemini-2.5-flash",
)

customer_question = input(
    "Which section of the report would you like to generate a work order for?\n"
)
result = crew.kickoff(inputs={"customer_question": customer_question})
print(result)