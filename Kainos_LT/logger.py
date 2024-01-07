
import traceback

class Logger:
        
    @staticmethod
    def log_relationship(entity1, entity2) -> None:
        print("\033[34m" + f'REL: {entity1.Type.name}:{entity1.Name} -> {entity2.Type.name}:{entity2.Name}' + "\033[0m")
        
    @staticmethod
    def log_init(entity) -> None:  
        print("\033[32m" + f'INIT: {entity.Id}:{entity.Type.name}:{entity.Name}:{entity.Url}' + "\033[0m")
        
    @staticmethod
    def log_warning(msg: str) -> None:  
        print("\033[33m" + f'WARN: {msg}' + "\033[0m")
        
    @staticmethod
    def log_error(entity, ex : Exception) -> None:  
        formatted_traceback = ''.join(traceback.format_exception(None, ex, ex.__traceback__))
        
        if (entity is None):
            print("\033[31m" + f'ERROR: {ex.args[0]}' + "\033[0m")
            return
                    
        print("\033[31m" + f'ERROR {entity.Type.name}:{entity.Name}:{formatted_traceback}' + "\033[0m")