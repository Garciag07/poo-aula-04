#!/usr/bin/env python3
import psutil
import platform
import argparse
import csv
import os
from datetime import datetime, timezone

def bytes2human(n):
    symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    i = 0
    while n >= 1024 and i < len(symbols) - 1:
        n /= 1024.0
        i += 1
    return f"{n:.2f} {symbols[i]}"

def write_metrics_csv(path, rows):
    file_exists = os.path.exists(path)
    write_header = not file_exists or os.path.getsize(path) == 0
    with open(path, mode='a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['datetime', 'metrica', 'valor', 'unidade'])
        for r in rows:
            writer.writerow(r)
    print(f"Métricas gravadas em {path}")

def main():
    parser = argparse.ArgumentParser(description='Exibe informações do sistema e opcionalmente grava métricas em CSV')
    parser.add_argument('--csv', action='store_true', help='Gravar métricas em CSV')
    parser.add_argument('--csv-file', default='metricas.csv', help='Caminho do arquivo CSV (padrão: metricas.csv)')
    parser.add_argument('--interval', type=float, default=1.0, help='Intervalo em segundos para medir CPU (padrão: 1.0)')
    parser.add_argument('--local-time', action='store_true', help='Usar timestamp local formatado (YYYY-MM-DD HH:MM:SS) em vez de ISO UTC')
    args = parser.parse_args()

    print("Informações do sistema")
    print(f"Sistema: {platform.system()} {platform.release()} ({platform.machine()})")

    print("\nMemória:")
    vm = psutil.virtual_memory()
    print(f"  Total: {bytes2human(vm.total)}")
    print(f"  Disponível: {bytes2human(vm.available)}")
    print(f"  Em uso: {bytes2human(vm.used)} ({vm.percent}%)")

    print("\nDisco (root /):")
    du = psutil.disk_usage('/')
    print(f"  Total: {bytes2human(du.total)}")
    print(f"  Usado: {bytes2human(du.used)} ({du.percent}%)")
    print(f"  Livre: {bytes2human(du.free)}")

    print("\nCPU:")
    cpu_pct = psutil.cpu_percent(interval=args.interval)
    print(f"  Percent (interval={args.interval}s): {cpu_pct}%")
    print(f"  Contagem lógica: {psutil.cpu_count(logical=True)}")
    print(f"  Contagem física: {psutil.cpu_count(logical=False)}")

    if args.csv:
        if args.local_time:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = datetime.now(timezone.utc).isoformat()
        rows = [
            (timestamp, 'memory_total', vm.total, 'bytes'),
            (timestamp, 'memory_available', vm.available, 'bytes'),
            (timestamp, 'memory_used_percent', vm.percent, 'percent'),
            (timestamp, 'disk_total', du.total, 'bytes'),
            (timestamp, 'disk_used_percent', du.percent, 'percent'),
            (timestamp, 'disk_free', du.free, 'bytes'),
            (timestamp, 'cpu_percent', cpu_pct, 'percent'),
        ]
        write_metrics_csv(args.csv_file, rows)

if __name__ == '__main__':
    main()

