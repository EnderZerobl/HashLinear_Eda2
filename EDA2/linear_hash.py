import json
import random
from dataclasses import dataclass, field
from typing import Optional, List
import matplotlib.pyplot as plt

@dataclass
class Page:
    capacity: int
    records: List[int] = field(default_factory=list)
    overflow: Optional["Page"] = None

    def is_full(self) -> bool:
        return len(self.records) >= self.capacity

    def overflow_depth(self) -> int:
        return 0 if self.overflow is None else 1 + self.overflow.overflow_depth()

class LinearHash:
    def __init__(self, page_capacity: int = 10, max_load_factor: float = 0.75):
        self.P: int = page_capacity
        self.alpha_max: float = max_load_factor
        self.level: int = 0          
        self.pointer: int = 0         
        self.pages: List[Page] = [Page(self.P)] 
        self.total_records: int = 0
        self.total_allocated_pages: int = 1
        self.disk_accesses: int = 0
        self.splits_done: int = 0
        self.successful_lookups: int = 0
        self.failed_lookups: int = 0
        self.accesses_successful: int = 0
        self.accesses_failed: int = 0

    def _hash(self, key: int, level: int) -> int:
        return key % (2 ** (level + 1))

    def _address(self, key: int) -> int:
        addr = key % (2 ** self.level)
        return self._hash(key, self.level) if addr < self.pointer else addr

    def load_factor(self) -> float:
        denom = self.total_allocated_pages * self.P
        return (self.total_records / denom) if denom > 0 else 0.0

    def _perform_split(self):
        self.splits_done += 1
        old_page = self.pages[self.pointer]
        new_page = Page(self.P)
        self.pages.append(new_page)
        
        all_records = []
        pg = old_page
        while pg:
            all_records.extend(pg.records)
            pg = pg.overflow
            
        self.pages[self.pointer] = Page(self.P)
        self.total_records -= len(all_records)
        self._recalc_allocated_pages()

        new_level = self.level + 1
        for key in all_records:
            dest = self.pages[self.pointer] if (key % (2 ** (new_level + 1))) == self.pointer else new_page
            
            curr = dest
            while curr.is_full():
                if curr.overflow is None:
                    curr.overflow = Page(self.P)
                    self.total_allocated_pages += 1
                curr = curr.overflow
            curr.records.append(key)
            self.total_records += 1

        self.pointer += 1
        if self.pointer >= (2 ** self.level):
            self.level += 1
            self.pointer = 0

    def _recalc_allocated_pages(self):
        self.total_allocated_pages = sum(1 + p.overflow_depth() for p in self.pages)

    def insert(self, key: int) -> dict:
        addr = self._address(key)
        pg = self.pages[addr]
        op_accesses = 0

        while True:
            op_accesses += 1
            self.disk_accesses += 1
            if not pg.is_full():
                pg.records.append(key)
                self.total_records += 1
                break
            if pg.overflow is None:
                pg.overflow = Page(self.P)
                self.total_allocated_pages += 1
                self.disk_accesses += 1  
                op_accesses += 1
            pg = pg.overflow
                
        splits_this_op = []
        while self.load_factor() > self.alpha_max:
            splits_this_op.append(self.pointer)
            self._perform_split()

        return {"key": key, "address": addr, "accesses": op_accesses, "splits": splits_this_op}

    def lookup(self, key: int) -> dict:
        addr = self._address(key)
        pg = self.pages[addr]
        op_accesses = 0
        
        while pg:
            op_accesses += 1
            self.disk_accesses += 1
            if key in pg.records:
                self.successful_lookups += 1
                self.accesses_successful += op_accesses
                return {"key": key, "found": True, "address": addr, "accesses": op_accesses}
            pg = pg.overflow

        self.failed_lookups += 1
        self.accesses_failed += op_accesses
        return {"key": key, "found": False, "address": addr, "accesses": op_accesses}

    def metrics(self) -> dict:
        total_primary = len(self.pages)
        overflow_pages = self.total_allocated_pages - total_primary
        total_capacity = self.total_allocated_pages * self.P

        avg_succ = self.accesses_successful / self.successful_lookups if self.successful_lookups else 0.0
        avg_fail = self.accesses_failed / self.failed_lookups if self.failed_lookups else 0.0
        space_util = self.total_records / total_capacity if total_capacity else 0.0
        over_pct = (overflow_pages / self.total_allocated_pages * 100) if self.total_allocated_pages else 0.0

        return {
            "level": self.level, "pointer": self.pointer,
            "total_records": self.total_records, "primary_pages": total_primary,
            "overflow_pages": overflow_pages, "total_allocated_pages": self.total_allocated_pages,
            "load_factor": self.load_factor(), "space_utilization": space_util,
            "overflow_pct": over_pct, "splits_done": self.splits_done,
            "total_disk_accesses": self.disk_accesses,
            "avg_accesses_successful": avg_succ, "avg_accesses_failed": avg_fail,
        }

    def page_state(self) -> List[dict]:
        res = []
        for i, pg in enumerate(self.pages):
            info = {"index": i, "records": list(pg.records), "capacity": self.P, "overflow_chain": []}
            ov = pg.overflow
            while ov:
                info["overflow_chain"].append({"records": list(ov.records)})
                ov = ov.overflow
            res.append(info)
        return res

    def export_json(self) -> str:
        return json.dumps({"metrics": self.metrics(), "pages": self.page_state()}, ensure_ascii=False)

def rodar_bateria(p_vals, alpha_vals, chaves_insert, chaves_succ, chaves_fail, nome_bateria):
    resultados = []
    total_scenarios = len(p_vals) * len(alpha_vals)
    current = 0
    
    print(f"\n{'='*50}\nIniciando: {nome_bateria}\n{'='*50}")
    
    for P in p_vals:
        for alpha in alpha_vals:
            current += 1
            pct = (current / total_scenarios) * 100
            print(f"[{pct:6.2f}%] Cenário {current}/{total_scenarios}: P={P:<4} | alpha_max={alpha:.2f}")
            
            lh = LinearHash(P, alpha)
            for k in chaves_insert: lh.insert(k)
            for k in chaves_succ: lh.lookup(k)
            for k in chaves_fail: lh.lookup(k)
                
            m = lh.metrics()
            resultados.append({
                "P": P, "alpha": alpha, 
                "avg_succ": m['avg_accesses_successful'],
                "avg_fail": m['avg_accesses_failed'], 
                "space_util": m['space_utilization'],
                "overflow_pct": m['overflow_pct'], 
                "overflow_count": m['overflow_pages'],
                "tipo": nome_bateria
            })
    return resultados

def imprimir_tabela(resultados, titulo):
    print("\n" + "=" * 88)
    print(f"{titulo:^88}")
    print("=" * 88)
    header = f" {'P':<5} | {'alpha':<5} | {'Busca Suc.':<11} | {'Busca Falha':<11} | {'Uso Espaço':<10} | {'% Overflow':<11} | {'Total Over.'}"
    print(header)
    print("-" * 88)
    for r in resultados:
        row = f" {r['P']:<5} | {r['alpha']:<5.2f} | {r['avg_succ']:<11.3f} | {r['avg_fail']:<11.3f} | {r['space_util']:<10.4f} | {r['overflow_pct']:<10.2f}% | {r['overflow_count']}"
        print(row)
    print("=" * 88)

def gerar_graficos_linhas(resultados, p_unique, alphas, prefixo):
    sty_cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    sty_markers = ['o', 's', '^', 'D', 'v', 'P']
    
    plt.figure(figsize=(9, 6))
    for i, alpha in enumerate(alphas):
        y_data = [r["overflow_pct"] for r in resultados if r["alpha"] == alpha]
        plt.plot(p_unique, y_data, color=sty_cores[i%len(sty_cores)], marker=sty_markers[i%len(sty_markers)], label=rf'$\alpha^{{max}} = {alpha}$', linewidth=2)
    plt.title(f'Impacto do Tamanho da Página no Overflow ({prefixo})')
    plt.xlabel('Tamanho da Página (P)')
    plt.ylabel('Transbordamento (%)')
    plt.xticks(p_unique)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.savefig(f'{prefixo}_grafico_overflow.png', dpi=300, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(9, 6))
    for i, alpha in enumerate(alphas):
        y_data = [r["avg_succ"] for r in resultados if r["alpha"] == alpha]
        plt.plot(p_unique, y_data, color=sty_cores[i%len(sty_cores)], marker=sty_markers[i%len(sty_markers)], label=rf'$\alpha^{{max}} = {alpha}$', linewidth=2)
    plt.title(f'Custo de Busca em Relação a P ({prefixo})')
    plt.xlabel('Tamanho da Página (P)')
    plt.ylabel('Média de Acessos a Disco')
    plt.xticks(p_unique)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.savefig(f'{prefixo}_grafico_custo_busca.png', dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    NUM_INSERTS = 100_000
    NUM_LOOKUPS_SUCCESS = 5_000
    NUM_LOOKUPS_FAIL = 5_000
        
    MAX_KEY_VAL = 2_000_000 
    all_keys = random.sample(range(1, MAX_KEY_VAL), NUM_INSERTS + NUM_LOOKUPS_FAIL)
    insert_keys, fail_keys = all_keys[:NUM_INSERTS], all_keys[NUM_INSERTS:]
    success_keys = random.sample(insert_keys, NUM_LOOKUPS_SUCCESS)

    P_prop = [10, 50, 100]
    alpha_prop = [0.60, 0.75, 0.90]
    res_prop = rodar_bateria(P_prop, alpha_prop, insert_keys, success_keys, fail_keys, "BATERIA PROPOSTA")

    P_est = [5, 25, 200, 500, 1000]
    alpha_est = [0.40, 0.50, 0.85, 0.95, 0.99]
    res_est = rodar_bateria(P_est, alpha_est, insert_keys, success_keys, fail_keys, "BATERIA ESTENDIDA")

    print("\n[100.00%] Todas as simulações concluídas!\n")
    imprimir_tabela(res_prop, "TABELA DE RESULTADOS: BATERIA PROPOSTA")
    imprimir_tabela(res_est, "TABELA DE RESULTADOS: BATERIA ESTENDIDA")

    gerar_graficos_linhas(res_prop, P_prop, alpha_prop, "proposta")
    gerar_graficos_linhas(res_est, P_est, alpha_est, "estendida")

    plt.figure(figsize=(10, 6))
    x_prop = [r['space_util'] for r in res_prop]
    y_prop = [r['avg_succ'] for r in res_prop]
    
    x_est = [r['space_util'] for r in res_est]
    y_est = [r['avg_succ'] for r in res_est]

    plt.scatter(x_prop, y_prop, color='#1f77b4', s=80, alpha=0.8, edgecolors='black', label='Bateria Proposta')
    plt.scatter(x_est, y_est, color='#ff7f0e', s=80, alpha=0.8, edgecolors='black', marker='^', label='Bateria Estendida')

    plt.title('Gráfico Comparativo Geral: O Trade-off Tempo vs. Espaço', fontsize=14)
    plt.xlabel('Utilização de Espaço Real (Fração)', fontsize=12)
    plt.ylabel('Custo de Busca (Média de Acessos a Disco)', fontsize=12)
    worst_time = max(res_est, key=lambda r: r['avg_succ'])
    best_time = min(res_est, key=lambda r: r['avg_succ'])

    plt.annotate(f"Pior Desempenho\n(P={worst_time['P']}, α={worst_time['alpha']})", 
                 xy=(worst_time['space_util'], worst_time['avg_succ']), 
                 xytext=(worst_time['space_util']-0.15, worst_time['avg_succ']-0.5), 
                 arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5))
                 
    plt.annotate(f"Melhor Desempenho\n(P={best_time['P']}, α={best_time['alpha']})", 
                 xy=(best_time['space_util'], best_time['avg_succ']), 
                 xytext=(best_time['space_util']+0.05, best_time['avg_succ']+1.0), 
                 arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5))

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='upper right')
    plt.savefig('comparativo_tradeoff_geral.png', dpi=300, bbox_inches='tight')
    plt.close()