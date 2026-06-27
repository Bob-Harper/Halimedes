import pkgutil
import inspect
import importlib
from reflex.reflexive_layer import Reflex

def load_all_reflexes():
    reflexes = []

    # Iterate over all modules in this package
    package = __name__
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{package}.{module_name}")

        # Find all classes in the module that subclass Reflex
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Reflex) and obj is not Reflex:
                reflexes.append(obj())

    return reflexes
