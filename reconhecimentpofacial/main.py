from banco import init_db,list_people,delete_person
from cadastro import register
from reconhecimento import recognize
from interface import load_model,menu

def main():
    init_db()
    try: model=load_model()
    except (FileNotFoundError,RuntimeError) as e:
        print(f"Erro de modelo: {e}\nConsulte o README para baixar os pesos."); return
    while True:
        op=menu()
        try:
            if op=="1":
                name=input("Nome ou ID: ").strip()
                if not name: print("Nome/ID vazio."); continue
                register(name,model)
            elif op=="2": recognize(model)
            elif op=="3":
                people=list_people()
                print("\n".join(f"ID {p['id']} | {p['nome']} | {p['data_cadastro']}" for p in people) if people else "Nenhum cadastro.")
            elif op=="4":
                for p in list_people(): print(f"ID {p['id']} | {p['nome']}")
                raw=input("ID numérico para excluir (ENTER cancela): ").strip()
                if raw:
                    if not raw.isdigit(): print("ID inválido.")
                    else: print("Excluído." if delete_person(int(raw)) else "ID não encontrado.")
            elif op=="5": break
            else: print("Escolha de 1 a 5.")
        except (ValueError,RuntimeError,OSError) as e: print(f"Operação não concluída: {e}")
if __name__=="__main__": main()
