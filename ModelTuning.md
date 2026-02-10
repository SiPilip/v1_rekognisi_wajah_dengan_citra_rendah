v6.4.1
knn_model = KNeighborsClassifier(n_neighbors=5, weights='distance', metric='euclidean')
svm_model = SVC(kernel='linear', probability=True, C=1.0)

v6.4.2
knn_model = KNeighborsClassifier(n_neighbors=12, weights='distance', metric='euclidean')
svm_model = SVC(kernel='linear', probability=True, C=10.0)

v6.4.3
knn_model = KNeighborsClassifier(n_neighbors=1, weights='distance', metric='euclidean')
svm_model = SVC(kernel='linear', probability=True, C=1000.0)

v6.4.4
knn_model = KNeighborsClassifier(n_neighbors=1, weights='distance', metric='manhattan')
svm_model = SVC(kernel='rbf', C=10.0, gamma='scale', probability=True)

v6.4.5
knn_model = KNeighborsClassifier(n_neighbors=3, weights='distance', metric='manhattan')
svm_model = SVC(kernel='linear', C=100.0, probability=True)
