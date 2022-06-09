import pkgutil
from abc import ABC
import sys
from django.core.management.base import BaseCommand, CommandError
from api.management import commands
from api.utils import populate_model

thismodule = sys.modules[__name__]
print(thismodule)


class Command(BaseCommand, ABC):
    help = "load all static objects into the database"

    def handle(self, *args, **options):
        all_modules = []
        importer = None

        #  get all the module files containing the different categories
        for imp, mod_name, ispkg in pkgutil.iter_modules(commands.__path__):
            importer = imp
            all_modules.append(mod_name)

        # exclude this module if among the files specified as it is an execution file
        if all_modules.count(thismodule.__name__.split('.')[-1]) > 0:
            all_modules.remove(thismodule.__name__.split('.')[-1])
            # print(all_modules)

        for name in all_modules:
            print(name, f"{name} has been loaded")
            module = importer.find_module(name).load_module(name)
            print(module, f"this module is included=====")
            if module:
                model = module.obj.get("model")
                data = module.obj.get("data")
                for d in data:
                    try:
                        print(model, d)
                        obj = model()
                        obj = populate_model(d, obj)
                        obj.save()
                        # model.objects.create(name=d.name)
                        print(f'{model} instance created')
                    except Exception as e:
                        print(
                            f"There was an exception for {name}=====>>>>>> {e}")
                        continue
                    self.stdout.write(self.style.SUCCESS(
                        'Entities were created successfully'))
