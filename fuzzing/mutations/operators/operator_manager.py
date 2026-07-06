from fuzzing.mutations.operators.roleplay import RoleplayOperator
from fuzzing.mutations.operators.authority import AuthorityOperator
from fuzzing.mutations.operators.persona import PersonaOperator
from fuzzing.mutations.operators.context_switch import ContextSwitchOperator
from fuzzing.mutations.operators.prompt_leakage import PromptLeakageOperator
from fuzzing.mutations.operators.translation import TranslationOperator
from fuzzing.mutations.operators.base64 import Base64Operator
from fuzzing.mutations.operators.rot13 import ROT13Operator
from fuzzing.mutations.operators.unicode import UnicodeOperator
from fuzzing.mutations.operators.typoglycemia import TypoglycemiaOperator
from fuzzing.mutations.operators.markdown import MarkdownOperator
from fuzzing.mutations.operators.xml import XMLOperator
from fuzzing.mutations.operators.json_operator import JSONOperator
from fuzzing.mutations.operators.indirect import IndirectInjectionOperator
from fuzzing.mutations.operators.chain_of_thought import ChainOfThoughtOperator

class OperatorManager:

    def __init__(self):

        self.operators = [RoleplayOperator(),AuthorityOperator(),PersonaOperator(),ContextSwitchOperator(),PromptLeakageOperator(),
                          TranslationOperator(),Base64Operator(),ROT13Operator(),
                          UnicodeOperator(),TypoglycemiaOperator(),MarkdownOperator(),
                          XMLOperator(),JSONOperator(),IndirectInjectionOperator(),ChainOfThoughtOperator(),]

    def get_all(self):
        """
        Returns every available mutation operator.
        """

        return self.operators

    def get_random(self):
        """
        Returns one random operator.
        """

        import random

        return random.choice(self.operators)