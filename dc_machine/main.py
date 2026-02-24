from base import DCMachine

def main() -> None:
    RA:  float = 0.2
    RF:  float = 0.2
    V:   float = 110
    N:   float = 1800
    PHI: float = 0.12
    K:   float = 1

    my_machine_1: DCMachine = DCMachine(RA, RF, V, N, PHI, K)
    my_machine_2: DCMachine = DCMachine(2, RF, V, N, PHI, K)

    print(f"Machine 1 -> Armature resistance: {my_machine_1.armature_resistance}")
    print(f"Machine 2 -> Armature resistance: {my_machine_2.armature_resistance}")


if __name__ == "__main__":
    main()
