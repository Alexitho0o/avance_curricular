# Estado base Git

- Rama observada: `backup/pre-sync-fix-20260410-avance`
- HEAD observado: `a95cb3ab42e936cce99c2db0a9572dae90e8eec6`
- HEAD 3B-A observado previamente: `f7d6c2802eed3aa2d18d9538cde3b87586266ab3`
- Upstream local: `origin/backup/pre-sync-fix-20260410-avance`
- HEAD upstream local: `6e15e063b85ee4b8b8d8937db5dc050a1833253b`
- Merge-base: `fe6fb6c549c5634a22eda2f8dcd5dbed6ed103e1`
- Ahead/behind: `1/1`
- origin/HEAD local: `NO_REGISTRADO`
- Status: `## backup/pre-sync-fix-20260410-avance...origin/backup/pre-sync-fix-20260410-avance [ahead 1, behind 1]`

Hallazgo: el HEAD actual difiere del HEAD reportado en 3B-A. Esto refuerza la decision de no integrar desde la rama backup actual y de crear posteriormente una rama limpia desde base confirmada.
