
import traceback

class Logger:
    
    @staticmethod
    def log_relationship(entity1, entity2) -> None:
        print(f'{entity1.Type.name}:{entity1.Name} pridėtas į {entity2.Type.name}:{entity2.Name}')
        
    @staticmethod
    def log_init(entity) -> None:  
        print(f'{entity.Id} sukurtas elementas {entity.Type.name}:{entity.Name}:{entity.Url}')
        
    @staticmethod
    def log_error(entity, ex : Exception) -> None:  
        formatted_traceback = ''.join(traceback.format_exception(None, ex, ex.__traceback__))
        
        if (entity is None):
            try:
                print(f'ERROR: {ex.args[0]}')
            except:
                print(f'ERROR: {ex.msg}')
            return
                    
        print(f'ERROR {entity.Type.name}:{entity.Name} ; {formatted_traceback}')