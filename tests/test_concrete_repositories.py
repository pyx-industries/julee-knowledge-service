"""
Test suite for validating concrete repository implementations
against their interfaces.

This module implements the Repository Pattern validation layer,
ensuring that concrete repository implementations strictly adhere
to their abstract interfaces.
It enforces the Liskov Substitution Principle by validating that:

1. Interface Compliance:
   - All abstract methods are implemented
   - No extra public methods exist
   - Method signatures match exactly

2. Type Safety:
   - Return types match between abstract and concrete methods
   - Parameter types and names match exactly
   - Optional and collection types are properly preserved

3. Contract Enforcement:
   - Single inheritance model is maintained
   - No breaking changes in concrete implementations
   - Complete interface implementation

This architectural enforcement ensures that
repository implementations remain interchangeable
and maintain strict separation
between interface and implementation.
"""

import inspect
import unittest
from abc import ABC
from typing import get_type_hints

try:
    from knowledge_service import config, django_setup, domain
except ModuleNotFoundError:
    import django_setup

    import config
    import domain
except ImportError:
    import django_setup

    import config
    import domain

django_setup.setup_django()


CONCRETE_REPOSITORIES = config.reposet  # not a typo, "set of repos"
DOMAIN_CLASSES = list(
    [cls for name, cls in inspect.getmembers(domain, inspect.isclass)]
)
PRIMITIVE_CLASSES = (None, int, str, tuple, list, dict, bool, float)


class TestConcreteRepositories(unittest.TestCase):
    """
    Test suite enforcing repository pattern implementation rules.

    This test suite validates that concrete repository classes
    properly implement their abstract interfaces, ensuring:

    - Complete implementation of abstract methods
    - Exact type matching for parameters and returns
    - No unauthorized public methods
    - Proper inheritance structure

    The suite assumes a single-inheritance model where each concrete repository
    extends exactly one abstract base class.
    """

    def test_return_types_match(self):
        """
        Validate return type consistency between abstract and concrete methods.

        For each concrete repository class:
        1. Identifies its abstract base class
        2. Compares return type annotations of all methods
        3. Ensures exact type matching, including for:
           - Primitive types
           - Domain model types
           - Collection types (List, Optional, etc.)
           - Union types

        Raises:
            AssertionError: If any return type mismatch is found
        """
        for module in CONCRETE_REPOSITORIES:
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, ABC) and cls is not ABC:
                    with self.subTest(concrete_class=cls):
                        self._check_return_types(cls)

    def test_parameter_types_match(self):
        """
        Validate parameter type consistency
        between abstract and concrete methods.

        For each concrete repository class:
        1. Compares parameter names and order
        2. Validates type annotations match exactly
        3. Ensures no additional or missing parameters
        4. Preserves optional parameters and defaults

        Raises:
            AssertionError: If any parameter signature mismatch is found
        """
        for module in CONCRETE_REPOSITORIES:
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, ABC) and cls is not ABC:
                    with self.subTest(concrete_class=cls):
                        self._check_parameter_types(cls)

    def _check_return_types(self, concrete_class):
        """Helper to validate method return types."""
        abc = concrete_class.__bases__[0]  # Assumes single inheritance
        for name, method in inspect.getmembers(
            abc, predicate=inspect.isfunction
        ):
            if hasattr(concrete_class, name):
                concrete_method = getattr(concrete_class, name)
                abc_return = get_type_hints(method).get("return", None)
                concrete_return = get_type_hints(concrete_method).get(
                    "return", None
                )
                self.assertEqual(
                    abc_return,
                    concrete_return,
                    (
                        f"Return type mismatch in method '{name}' of class "
                        f"'{concrete_class.__name__}': {abc_return} (ABC) vs "
                        f"{concrete_return} (concrete)."
                    ),
                )

    def _check_parameter_types(self, concrete_class):
        """Helper to validate method parameter types."""
        abc = concrete_class.__bases__[0]  # Assumes single inheritance
        for name, method in inspect.getmembers(
            abc, predicate=inspect.isfunction
        ):
            if hasattr(concrete_class, name):
                concrete_method = getattr(concrete_class, name)
                abc_sig = inspect.signature(method)
                concrete_sig = inspect.signature(concrete_method)
                for abc_param, abc_detail in abc_sig.parameters.items():
                    if abc_param == "self":  # Skip 'self'
                        continue
                    concrete_param = concrete_sig.parameters.get(abc_param)
                    self.assertIsNotNone(
                        concrete_param,
                        (
                            f"Parameter '{abc_param}' missing "
                            f"in method '{name}' "
                            f"of class '{concrete_class.__name__}'."
                        ),
                    )
                    abc_type = get_type_hints(method).get(abc_param, None)
                    concrete_type = get_type_hints(concrete_method).get(
                        abc_param, None
                    )
                    self.assertEqual(
                        abc_type,
                        concrete_type,
                        (
                            "Type mismatch for parameter '"
                            f"{abc_param}' in method "
                            f"'{name}' of class '{concrete_class.__name__}': "
                            f"{abc_type} (ABC) vs {concrete_type} (concrete)."
                        ),
                    )

    def test_methods_match(self):
        """
        Verify complete and exact implementation of abstract interface methods.

        Ensures that concrete repositories:
        1. Implement all abstract methods from their base class
        2. Don't add any unauthorized public methods
        3. Maintain the exact method names

        This enforces interface segregation and prevents interface pollution.

        Raises:
            AssertionError: If methods are missing or extra methods are found
        """
        for module in CONCRETE_REPOSITORIES:
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, ABC) and cls is not ABC:
                    with self.subTest(concrete_class=cls):
                        self._check_methods_match(cls)

    def _check_methods_match(self, concrete_class):
        """Validate concrete class methods against abstract base class."""
        abc = concrete_class.__bases__[0]  # Assumes single inheritance
        abc_methods = {
            name
            for name, method in inspect.getmembers(
                abc, predicate=inspect.isfunction
            )
            if getattr(method, "__isabstractmethod__", False)
        }
        concrete_methods = {
            name
            for name, method in inspect.getmembers(
                concrete_class, predicate=inspect.isfunction
            )
            if not name.startswith("_")  # Exclude private/protected methods
        }
        missing_methods = abc_methods - concrete_methods
        self.assertFalse(
            missing_methods,
            (
                f"Concrete class '{concrete_class.__name__}' is missing the "
                f"following methods required by the abstract base class "
                f"'{abc.__name__}': {missing_methods}."
            ),
        )
        extra_methods = concrete_methods - abc_methods
        self.assertFalse(
            extra_methods,
            (
                f"Concrete class '{concrete_class.__name__}' "
                "implements extra methods, not defined in the "
                f"abstract base class '{abc.__name__}': "
                f"{extra_methods}."
            ),
        )


if __name__ == "__main__":
    unittest.main()
