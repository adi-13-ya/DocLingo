# Architecture Diagrams

This folder contains PlantUML diagrams documenting the DocLingo system architecture.

## Diagrams

- **RAG_COMPONENTS.puml** - RAG system component diagram
- **RAG_PIPELINE.puml** - RAG pipeline flow diagram
- **RAG_SEQUENCE.puml** - RAG sequence diagram

## Viewing Diagrams

To view these PlantUML diagrams:

1. **Online**: Use [PlantUML Online Server](http://www.plantuml.com/plantuml/uml/)
2. **VS Code**: Install the PlantUML extension
3. **Command Line**: Install PlantUML and run `plantuml diagram.puml`

## Generating PNG/SVG

```bash
# Install PlantUML first
plantuml -tpng *.puml
plantuml -tsvg *.puml
```
