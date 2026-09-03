# BatchedBayes
Temp notes for Bao test

Ran script = 

python init_linear.py --batch_method thompson --batch_size 10 --max_per_category 1 --mesh_size 21 --fine_mesh_size 11 --top_k_categories 10

python init_linear.py --batch_method greedy_ei_screening --batch_size 10 --max_per_category 1 --mesh_size 21 --fine_mesh_size 11 --top_k_categories 10

python init_linear.py --batch_method thompson --batch_size 5 --mesh_size 21 --fine_mesh_size 11 --top_k_categories 12
