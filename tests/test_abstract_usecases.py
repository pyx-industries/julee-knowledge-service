"""
Test suite for validating use cases.

This module ensures that all use cases follow the required patterns:
- Must have an execute() method
- Parameters must be either primitives or formal request types
- Return types must be explicitly defined and valid
  (primitives or formal response types).
- Type validation includes handling of Optional, Union, and collection types

These tests maintain architectural boundaries by ensuring use cases
only depend on formal interfaces (requests and responses)
and primitive types.
"""

import inspect
import unittest
from typing import Union, get_args, get_origin

try:
    import knowledge_service.usecases as usecases
    from knowledge_service.interfaces import requests, responses
except ModuleNotFoundError:
    import usecases as usecases
    from interfaces import requests, responses

REQUEST_CLASSES = [
    cls for name, cls in inspect.getmembers(requests, inspect.isclass)
]
PRIMITIVE_CLASSES = (None, int, str, tuple, list, dict, bool, float)

# Both primitive types and response interfaces are valid return types
VALID_RETURN_TYPES = PRIMITIVE_CLASSES + tuple(
    cls for name, cls in inspect.getmembers(responses, inspect.isclass)
)


class TestUsecases(unittest.TestCase):
    """
    Test suite for validating use case method signatures
    and type constraints.
    """

    def test_all_usecases_have_execute_method(self):
        """
        Verify that all use case classes implement
        an executable execute() method.

        This test ensures that:
        1. Each use case class has an 'execute' attribute
        2. The 'execute' attribute is a callable method
        """
        for name, obj in inspect.getmembers(usecases, inspect.isclass):
            if obj.__module__ == usecases.__name__:
                self.assertTrue(
                    hasattr(obj, "execute"),
                    f"Class {name} is missing 'execute' method",
                )
                execute_method = getattr(obj, "execute")
                self.assertTrue(
                    callable(execute_method),
                    f"Method 'execute' in class {name} is not callable",
                )

    def test_usecase_execute_method_parameter_types(self):
        """
        Validate parameter types of execute() methods in all use cases.

        Parameters must be one of:
        - None
        - Primitive types (int, str, etc.)
        - Formal interface types from interfaces module

        This enforces clean architecture by preventing dependencies on
        concrete implementations.
        """
        for name, obj in inspect.getmembers(usecases, inspect.isclass):
            if obj.__module__ == usecases.__name__:
                execute_method = getattr(obj, "execute")
                signature = inspect.signature(execute_method)
                for param in signature.parameters.values():
                    param_type = param.annotation
                    # it's OK to take no parameters, that's allowed
                    if param_type is not inspect.Parameter.empty:
                        # primative types are allowed too
                        primative_types = PRIMITIVE_CLASSES
                        if param_type is None or param_type in primative_types:
                            continue
                        # Handle fully qualified interface types
                        if hasattr(param_type, '__module__'):
                            module_path = param_type.__module__.split('.')
                            if (len(module_path) >= 1 and 
                                module_path[-1] == 'requests'):
                                continue

                        # if not a primative (or None),
                        # must be a formal interface
                        if param_type in REQUEST_CLASSES:
                            continue
                        # otherwise, sorry but...
                        fail_msg = (
                            f"Parameter {param.name} in 'execute' method "
                            f"of class {name} has invalid type: "
                            f"{param_type}\n(must be None, a primative, "
                            "or an instance from interfaces.*)"
                        )
                        self.fail(fail_msg)

    def test_execute_method_return_type(self):
        """
        Verify that execute() methods have valid return type annotations.

        Valid return types include:
        - None
        - Primitive types
        - Interface types
        - Collections (List, Optional, Union) of valid types

        Enforces explicit return type definitions and type safety.
        """
        for name, obj in inspect.getmembers(usecases, inspect.isclass):
            if obj.__module__ == usecases.__name__:
                execute_method = getattr(obj, "execute")
                signature = inspect.signature(execute_method)
                return_annotation = signature.return_annotation
                if return_annotation is inspect._empty:
                    fail_msg = (
                        f"Return type of 'execute' method in class {name} "
                        "is not defined, and must be. Mayhap -> bool ?"
                    )
                    print(
                        f"DEBUG: return type of {name} "
                        f"is {return_annotation}"
                    )
                    self.fail(fail_msg)
                if not self._is_valid_return_type(return_annotation):
                    fail_msg = (
                        f"Return type of 'execute' method in class {name} "
                        f"is invalid: {return_annotation}\n"
                        "(it needs to be None, a primitive type, "
                        "or formally defined in the interface module)"
                    )
                    self.fail(fail_msg)

    def _is_valid_return_type(self, return_annotation):
        """
        Recursively validate if a return type annotation is acceptable.

        Args:
            return_annotation: The type annotation to validate

        Returns:
            bool: True if the type is valid, False otherwise

        Valid types include:
        - Interface classes
        - Primitive types
        - Union/Optional of valid types
        - List of valid types
        - String literal type hints referencing valid types
        """
        # Handle string literal type hints
        if isinstance(return_annotation, str):
            # Check if it references a valid response type
            type_path = return_annotation.split('.')
            if len(type_path) >= 2 and type_path[-2] == 'responses':
                return True

        if return_annotation in VALID_RETURN_TYPES:
            return True

        # Handle class types that might be from responses module
        if hasattr(return_annotation, '__module__'):
            module_path = return_annotation.__module__.split('.')
            if module_path[-1] == 'responses':
                return True

        # Handle Union (Optional[T] is Union[T, None])
        if get_origin(return_annotation) is Union:
            inner_types = get_args(return_annotation)
            # Check if all inner types are valid
            return all(
                self._is_valid_return_type(inner_type)
                or inner_type is type(None)
                for inner_type in inner_types
            )
        # Handle List[T]
        if get_origin(return_annotation) is list:
            inner_type = get_args(return_annotation)[0]
            return self._is_valid_return_type(inner_type)

        # If none of the above, it's invalid
        return False


if __name__ == "__main__":
    unittest.main()
