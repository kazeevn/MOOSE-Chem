# Non-strict setup
## Background survey
Background survey:
1. SOTA diffusion models for solid state materials produce an abnormally high fraction of materials lacking symmetry. In the MP-20 dataset more than 98% of materials  have internal symmetry, while only ~70% produced by DiffCSP & FlowMM do.
2. Most atoms in stable materials occupy special Wyckoff positions, allowing encoding the crystal structure based on Wyckoff positions.
3. Wyckoff positions are discrete, and can be represented as categorical variables.
4. Existing generative models based on Wyckoff positions underperform the SOTA models in terms of stability, uniqueness, and novelty.
5. Existing generative models based on Wyckoff positions build their representation using Wyckoff letters and don't take into account the possible existence of multiple equvalent Wyckoff representations for the same crystal structure.
## Background question
How can we build a generative model based on Wyckoff positions that will faithfully reproduce the distribution of symmetry space groups and outperform the SOTA models in terms of stability, uniqueness, and novelty?
# Strict setup
## Background survey
Background survey:
1. SOTA diffusion models for solid state materials produce an abnormally high fraction of materials lacking symmetry. In the MP-20 dataset more than 98% of materials  have internal symmetry, while only ~70% produced by DiffCSP & FlowMM do.
2. Most atoms in stable materials occupy special Wyckoff positions, allowing encoding the crystal structure based on Wyckoff positions.
3. Wyckoff positions are discrete, and can be represented as categorical variables.
4. Existing generative models based on Wyckoff positions underperform the SOTA models in terms of stability, uniqueness, and novelty.
## Background question
How can we build a generative model that will faithfully reproduce the distribution of symmetry space groups and outperform the SOTA models in terms of stability, uniqueness, and novelty?
# Main Inspiration
The main inspiration is to represent a crystal as a permutation-invariant, unordered set of discrete tokens, where each token fuses a chemical element with a Wyckoff position. Wyckoff positions are encoded using site symmetry, whose definition is transferable between the space groups. Transformer model is used to autoregressively generate these tokens.
# Inspiration paper 1 title
WyCryst: Wyckoff inorganic crystal generator framework
# Relation between the main inspiration and the inspiration paper 1
This paper was the first generative model to use a Wyckoff position (WP)-based representation. However, it uses one-hot-encoding and VAE, limiting its performance. It also uses Wyckoff letters, whose definitions are not transferable between space groups.
# Inspiration paper 2 title
Attention is all you need
# Relation between the main inspiration and the inspiration paper 2
The paper introduces Transformer architecture: the widely succesful architecture for discrete sequential data.
# Inspiration paper 3 title
Accurate structure prediction of biomolecular interactions with AlphaFold 3
# Relation between the main inspiration and the inspiration paper 3
This paper inspires the training strategy of not strictly enforcing model invariance to different equivalent Wyckoff representations, but rather teaching it through data augmentation. In each training epoch, a randomly selected equivalent representation is used, allowing the model to learn the invariance implicitly.
# Main hypothesis
The paper hypothesizes that by representing a crystal as a permutation-invariant set of tokens (fusing chemical elements and Wyckoff positions) and using a purpose-built autoregressive Transformer model, it is possible to generate novel, diverse, and stable symmetric crystals that outperform existing generative methods. It is also hypothesized that this coordinate-free representation contains sufficient information to predict key material properties with performance competitive with models that use full atomic coordinates
# Experiments to Verify the Research Hypothesis
The hypothesis was tested through two main sets of experiments:
1. De Novo Crystal Generation: The model was trained on the MP-20 and MPTS-52 datasets and used to generate thousands of novel crystal structures. The quality of these structures was evaluated against several baseline models (e.g., DiffCSP++, CrystalFormer, WyCryst) using a suite of metrics, including the fraction of stable, unique, and novel structures (S.U.N.), as well as metrics specifically designed to assess symmetry, such as the fraction of symmetric structures (S.S.U.N.), the diversity of new structural templates, and the similarity of the generated space group distribution to the training data
2. Material Property Prediction: The model's ability to predict physical properties without coordinate information was tested. It was trained on the MP-20 and AFLOW datasets to predict properties like formation energy, band gap, thermal conductivity, and bulk modulus. Its performance (measured by Mean Absolute Error) was compared to established models that rely on full 3D structural information.
# Reasoning Process
bkg + insp1 + insp2 + insp3 = hyp
# Note
insp1: WP-based representation (ref: Zhu et al., 2024), Wyckoff letters and problems with them are not explained in the abstract; insp2: Transformer; insp3: Training with data augmentation for invariance, but not explained in the abstact.