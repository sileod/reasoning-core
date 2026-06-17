from reasoning_core.tasks.coreference import Coreference
import sys

def test_hops(level):
    print(f"\n{'='*40}\nLEVEL {level}\n{'='*40}")
    task = Coreference()
    for i in range(2):
        ex = task.generate_example(level=level)
        print(ex.prompt)
        print(f"Answer: {ex.answer}")
        
        # We can also extract the exact chain if we want, but let's just show the prompt
        print("-" * 20)

if __name__ == "__main__":
    test_hops(0)
    test_hops(2)
    test_hops(4)
