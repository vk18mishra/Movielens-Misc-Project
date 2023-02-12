from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
import streamlit as st
from scipy.sparse import csr_matrix
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.decomposition import KernelPCA

@st.experimental_memo
def clustering_kmeans(X):
    
    kmeans = KMeans(n_clusters=5, init='k-means++', max_iter=300, n_init=10, random_state=0)
    st.write("""- _Fitting Kmeans on resulting Dense Matrix after SVD_\n""")
    kmeans.fit(X)

    # Get the cluster labels
    labels = kmeans.labels_

    # Get the cluster centers
    cluster_centers = kmeans.cluster_centers_
    
    return labels

@st.experimental_memo
def nearest_neighbours_similar(X, main_df_copy, userii):
    # Create a NearestNeighbors object
    nn = NearestNeighbors(n_neighbors=11)

    # Fit the NearestNeighbors object to the data
    st.write("""- _Fitting KNN on resulting Dense Matrix after SVD_\n""")
    nn.fit(X)
    
    userii = int(userii)
    if userii < 72341: 
        userii = userii - 1
    else:
        userii = userii - 2
    # Find the k nearest neighbors for a specific data point
    index = userii
    distances, indices = nn.kneighbors([X[index]], return_distance=True)

    # The indices of the k nearest neighbors can be found in the indices array
    # print("Indices:",indices,'\nDistances:',distances[0])
    flag = 0
    for index_u in range(11):
        if indices[0][index_u] >= 72341: 
            indices[0][index_u] = indices[0][index_u] + 1

    similar_ui = main_df_copy.loc[indices[0]]
    similar_ui.insert(1, 'Distance', list(distances[0]))
    # similar_ui['Distance'] = list(distances[0])
    similar_ui = similar_ui.sort_values(by='Distance')
    similar_ui.rename(columns = {'rating':'Mean Rating'}, inplace = True)
    
    return similar_ui

@st.experimental_memo
def svd_on_usersgerne(main_df_copy):
    # create an instance of the StandardScaler class
    scaler = StandardScaler()

    st.write("""- _Standarizing(Centering the data) the values in UsersByGenre Table_\n""")
    # fit the scaler to the DataFrame
    scaler.fit(main_df_copy)

    # transform the DataFrame
    main_df_norm = scaler.transform(main_df_copy)

    st.write("""- _Converting the resulting table to Dataframe_\n""")
    # convert the normalized values back to a DataFrame
    main_df_norm = pd.DataFrame(main_df_norm, columns=main_df_copy.columns)
    
    st.write("""- _Creating a Sparse Matrix from it_\n""")
    # Create a sparse matrix
    sparse_matrix = csr_matrix(main_df_norm)

    st.write("""- _Performing SVD Decomposition on it_\n""")
    # Perform SVD on the sparse matrix
    svd = TruncatedSVD(n_components=5)
    # transformer = KernelPCA(n_components=2, kernel='linear')
    # X = transformer.fit_transform(sparse_matrix)
    X = svd.fit_transform(sparse_matrix)
    return X