# Journey Architecture OS — русская версия

**Journey Architecture OS — открытая операционная система для проектирования, измерения и управления путями клиентов и сотрудников (customer и employee journeys).**

Покрывает CJM, EJM, service design, journey management, governance, метрики и управление портфелем journeys. Поставляется как 15 вендор-нейтральных [Agent Skills](https://agentskills.io/specification) для ИИ-агентов и практиков.

Главная идея репозитория: перестать относиться к CJM/EJM как к красивой карте после воркшопа и сделать из journeys управляемую систему.

## Сквозной процесс

**Evidence → Actor → Journey Architecture → Current State → Service Blueprint → Moments that Matter → Metrics → Opportunities → Target Experience → Initiatives → Governance → Portfolio**

## Что отличает подход

- Любое существенное утверждение маркируется как `observed`, `inferred`, `hypothesis` или `unknown`.
- Journey имеет стабильный ID, владельца, версию, статус и дату ревью; каждое существенное изменение попадает в журнал с причиной, evidence и утверждающим.
- CJM и EJM строятся от целей и реального опыта человека, а не от внутренней оргструктуры.
- Service Blueprint отделён от CJM: карта показывает опыт, blueprint — механизм его доставки.
- Метрики образуют дерево с одним корнем — outcome актора; причинные связи между метриками записываются отдельно и имеют собственный статус доказательности.
- Opportunity backlog связан с evidence, root causes, owner и инициативами.
- Journey portfolio позволяет управлять десятками и сотнями journeys на уровне компании.

## Контракт и реестры (v1.1)

Единственный источник истины — [`skills/journey-architecture/references/ontology.md`](skills/journey-architecture/references/ontology.md): сущности, грамматика ID, перечисления, колонки реестров и правила ссылочной целостности. Каждый skill несёт сгенерированную из неё копию `references/conventions.md`, поэтому работает и при установке по одному.

Факты живут в CSV-реестрах со стабильными ID: акторы (`ACT-`), journeys (`DOM-`/`LFC-`/`JRN-`, уровни L0–L2), связи, узлы (`NOD-`: этап — L3, эпизод/шаг/взаимодействие внутри этапа — L4), evidence (`EVD-`), moments that matter (`MTM-`), метрики (`MET-`) и причинные связи между ними, opportunities (`OPP-`), инициативы (`INI-`), портфель, governance и журнал изменений (`CHG-`). CJM, blueprint и отчёты — представления поверх реестров, они ссылаются на ID, а не хранят данные.

Правило доказательности проверяется машинно: утверждение `observed` ссылается хотя бы на одну запись evidence со статусом `observed`, `inferred` — на `observed` или `inferred`; мнение стейкхолдеров (`stakeholder-input`) даёт максимум `hypothesis`. Текущее, целевое и переходное состояния — разные journeys, связанные через `baseline_journey_id`.

Полный сквозной пример одного journey — от брифа и evidence до метрик, opportunities, целевого состояния и аудита: [`examples/saas-onboarding/`](examples/saas-onboarding/).

## JourneyOps — операционный слой

Карта полезна, пока она актуальна. **JourneyOps** — часть системы, которая держит journeys живыми после картирования: владелец, версия, свежесть evidence, ритм ревью, метрики по этапам, связь opportunities с инициативами по всему портфелю. В репозитории это `journey-governance` + `journey-metrics` + `journey-portfolio-management`, а `journey-quality-audit` служит проверкой здоровья.

## Быстрый старт

Для широкого или неоднозначного запроса начинай с `experience-architecture`: он выбирает нужную последовательность остальных skills.

Для CJM:

`journey-architecture → journey-research → jobs-and-outcomes → customer-journey-mapping → moments-that-matter → journey-metrics → experience-opportunity-prioritization`

Для EJM:

`journey-architecture → journey-research → employee-journey-mapping → moments-that-matter → service-blueprinting → journey-metrics`

Для enterprise-модели:

`journey-architecture → journey-governance → journey-portfolio-management → journey-metrics → journey-quality-audit`

## Установка

```bash
python3 scripts/install_skills.py --all --target .agents/skills
```

Проверка:

```bash
make validate test evals-check
```

`make validate` сверяет skills, шаблоны реестров и примеры с онтологией и JSON Schemas из `schemas/`: заголовки, форматы ID, перечисления, ссылки между реестрами и подкреплённость `observed`. `make test` прогоняет валидатор на эталонных фикстурах и на намеренно сломанных копиях. `evals/` содержит кейсы маршрутизации (выбирает ли агент нужный skill по описанию) и поведенческие кейсы (улучшает ли skill результат); `make evals-check` проверяет их структуру, запуск на агенте — `python3 scripts/run_evals.py --mode routing` и `--mode behavior --repeats 3` (подробности в `docs/evaluations.md`). `make mutation` (локально, около 25 минут) измеряет, какие дефекты валидатор ловит на самом деле.

Основная документация написана на английском, чтобы репозиторий можно было публиковать международно. Методология не требует конкретного инструмента: её можно применять в Miro, FigJam, Smaply, spreadsheets, BI, Notion, Jira или собственной journey-management системе.
