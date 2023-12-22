
import traceback

class Logger:
    
    @staticmethod
    def log_relationship(entity1, entity2) -> None:
        print(f'REL: {entity1.Type.name}:{entity1.Name} -> {entity2.Type.name}:{entity2.Name}')
        
    @staticmethod
    def log_init(entity) -> None:  
        print(f'INIT: {entity.Id}:{entity.Type.name}:{entity.Name}:{entity.Url}')
        
    @staticmethod
    def log_warning(msg: str) -> None:  
        print(f'WARN: {msg}')
        
    @staticmethod
    def log_error(entity, ex : Exception) -> None:  
        formatted_traceback = ''.join(traceback.format_exception(None, ex, ex.__traceback__))
        
        if (entity is None):
            print(f'ERROR: {ex.args[0]}')
            return
                    
        print(f'ERROR {entity.Type.name}:{entity.Name}:{formatted_traceback}')