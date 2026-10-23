"""Carga masiva e idempotente de ejercicios.

Uso (desde la raíz del proyecto):

    .\\.venv\\Scripts\\python.exe seed_exercises.py

Es re-ejecutable: no duplica ejercicios que ya existan (compara por nombre).
"""

from db import SessionLocal, init_db
from models import Exercise
from models.enums import GrupoMuscularEnum
from repositories.exercise_repository import ExerciseRepository

# (nombre, descripción, grupo muscular)
DATA: list[tuple[str, str, GrupoMuscularEnum]] = [
    # PECHO
    ("Press de banca con barra", "Banco plano, agarre medio", GrupoMuscularEnum.PECHO),
    ("Press inclinado con mancuernas", "Banco inclinado 30-45 grados", GrupoMuscularEnum.PECHO),
    ("Press declinado", "Banco declinado con barra", GrupoMuscularEnum.PECHO),
    ("Aperturas en polea", "Cruces de polea para pectoral", GrupoMuscularEnum.PECHO),
    ("Fondos en paralelas", "Peso corporal, inclinación al frente", GrupoMuscularEnum.PECHO),
    ("Pec deck", "Máquina de aperturas convergentes", GrupoMuscularEnum.PECHO),
    # ESPALDA
    ("Dominadas", "Agarre prono, peso corporal", GrupoMuscularEnum.ESPALDA),
    ("Remo con barra", "Tronco inclinado, agarre prono", GrupoMuscularEnum.ESPALDA),
    ("Remo con mancuerna", "Un brazo, apoyo en banco", GrupoMuscularEnum.ESPALDA),
    ("Jalón al pecho", "Polea alta, agarre ancho", GrupoMuscularEnum.ESPALDA),
    ("Peso muerto convencional", "Barra desde el suelo, espalda neutra", GrupoMuscularEnum.ESPALDA),
    ("Remo en máquina", "Máquina sentado, agarre neutro", GrupoMuscularEnum.ESPALDA),
    # PIERNA
    ("Sentadilla con barra", "Barra alta, profundidad paralela", GrupoMuscularEnum.PIERNA),
    ("Prensa 45 grados", "Pies al ancho de hombros", GrupoMuscularEnum.PIERNA),
    ("Zancadas con mancuernas", "Paso alternado, rodilla alineada", GrupoMuscularEnum.PIERNA),
    ("Extensión de cuádriceps", "Máquina, extensión completa", GrupoMuscularEnum.PIERNA),
    ("Curl femoral", "Máquina tumbado o sentado", GrupoMuscularEnum.PIERNA),
    ("Elevación de gemelos", "De pie o sentado, rango completo", GrupoMuscularEnum.PIERNA),
    # HOMBRO
    ("Press militar con barra", "De pie o sentado, barra al frente", GrupoMuscularEnum.HOMBRO),
    ("Press con mancuernas", "Sentado, agarre neutro", GrupoMuscularEnum.HOMBRO),
    ("Elevaciones laterales", "Mancuernas, codo ligeramente flexionado", GrupoMuscularEnum.HOMBRO),
    ("Pájaros", "Mancuernas, tronco inclinado", GrupoMuscularEnum.HOMBRO),
    ("Face pull", "Polea alta con cuerda", GrupoMuscularEnum.HOMBRO),
    # BICEPS
    ("Curl con barra", "De pie, agarre supino", GrupoMuscularEnum.BICEPS),
    ("Curl alterno con mancuernas", "Supinación al subir", GrupoMuscularEnum.BICEPS),
    ("Curl martillo", "Agarre neutro", GrupoMuscularEnum.BICEPS),
    ("Curl en banco Scott", "Barra Z, apoyo en banco", GrupoMuscularEnum.BICEPS),
    ("Curl en polea", "Polea baja con barra", GrupoMuscularEnum.BICEPS),
    # TRICEPS
    ("Extensión en polea", "Polea alta con cuerda o barra", GrupoMuscularEnum.TRICEPS),
    ("Press francés", "Barra Z, acostado", GrupoMuscularEnum.TRICEPS),
    ("Fondos en banco", "Peso corporal, codos alineados", GrupoMuscularEnum.TRICEPS),
    ("Patada de tríceps", "Mancuerna, tronco inclinado", GrupoMuscularEnum.TRICEPS),
    ("Extensión sobre la cabeza", "Mancuerna o cuerda", GrupoMuscularEnum.TRICEPS),
    # ABDOMEN
    ("Crunch", "Suelo, flexión de tronco", GrupoMuscularEnum.ABDOMEN),
    ("Plancha", "Isométrico, cuerpo alineado", GrupoMuscularEnum.ABDOMEN),
    ("Elevación de piernas", "Colgado o tumbado", GrupoMuscularEnum.ABDOMEN),
    ("Russian twist", "Rotación de tronco, peso opcional", GrupoMuscularEnum.ABDOMEN),
    ("Abdominal en polea alta", "Arrodillado, flexión de tronco", GrupoMuscularEnum.ABDOMEN),
    # GLUTEO
    ("Hip thrust", "Barra o máquina, empuje de cadera", GrupoMuscularEnum.GLUTEO),
    ("Patada de glúteo", "Polea o máquina, extensión de cadera", GrupoMuscularEnum.GLUTEO),
    ("Puente de glúteo", "Suelo, peso corporal", GrupoMuscularEnum.GLUTEO),
    ("Sentadilla búlgara", "Pie trasero elevado", GrupoMuscularEnum.GLUTEO),
    ("Abducción en máquina", "Apertura de piernas sentado", GrupoMuscularEnum.GLUTEO),
    # FULL BODY
    ("Burpees", "Peso corporal, ritmo controlado", GrupoMuscularEnum.FULL_BODY),
    ("Clean and press", "Barra o mancuernas, movimiento completo", GrupoMuscularEnum.FULL_BODY),
    ("Kettlebell swing", "Bisagra de cadera, empuje de pelvis", GrupoMuscularEnum.FULL_BODY),
    ("Thruster", "Sentadilla frontal + press", GrupoMuscularEnum.FULL_BODY),
    ("Remo renegado", "Plancha con remo alterno", GrupoMuscularEnum.FULL_BODY),
]


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        repository = ExerciseRepository(db)
        created = 0
        skipped = 0

        for name, description, muscular_group in DATA:
            if repository.get_by_name(name):
                skipped += 1
                continue

            exercise = Exercise(
                name=name,
                description=description,
                muscular_group=muscular_group,
            )
            repository.create_new_exercise(exercise)
            created += 1

        print(f"Ejercicios creados: {created} | saltados (ya existían): {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
