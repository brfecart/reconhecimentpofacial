from banco import init_db,list_people,delete_person
from cadastro import register
from reconhecimento import recognize
from interface import load_model,menu

def main():
    try:
        init_db()
        model = load_model()
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Erro: {e}")
        return
    while True:
        op=menu()
        try:
            if op=="1":
                name=input("Nome ou ID: ").strip()
                if not name: print("Nome/ID vazio."); continue
                ok=input("A pessoa autorizou o uso do rosto (LGPD)? (s/n): ").strip().lower()
                if ok!="s": print("Cadastro cancelado: sem consentimento."); continue
                register(name,model,consentimento=True)
            elif op=="2": recognize(model)
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
