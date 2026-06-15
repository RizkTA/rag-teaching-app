from sklearn.decomposition import PCA

def project_embeddings(vectors):
    pca = PCA(n_components=2)
    projected = pca.fit_transform(vectors)
    return projected.tolist()
