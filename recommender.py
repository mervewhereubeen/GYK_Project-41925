from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

class MovieRecommender:
    def __init__(self, n_clusters=5):
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.scaler = StandardScaler()
    
    def prepare_data(self, movies_df):
        # Genre'leri one-hot encoding yap
        genre_dummies = pd.get_dummies(movies_df['genre'])
        
        # Yılları ölçeklendir
        years = movies_df[['year']].values
        years_scaled = self.scaler.fit_transform(years)
        
        # Özellikleri birleştir
        features = np.hstack([years_scaled, genre_dummies.values])
        return features
    
    def fit(self, movies_df):
        features = self.prepare_data(movies_df)
        self.kmeans.fit(features)
    
    def get_recommendations(self, user_history, movies_df, n_recommendations=5):
        if movies_df.empty or user_history.empty:
            return pd.DataFrame()
            
        # Kullanıcının izlediği filmlerin özelliklerini hazırla
        user_features = self.prepare_data(user_history)
        user_clusters = self.kmeans.predict(user_features)
        
        # En sık görülen cluster'ı bul
        preferred_cluster = max(set(user_clusters), key=list(user_clusters).count)
        
        # Tüm filmlerin cluster'larını bul
        all_features = self.prepare_data(movies_df)
        all_clusters = self.kmeans.predict(all_features)
        
        # İzlenmemiş ve tercih edilen cluster'daki filmleri bul
        watched_ids = set(user_history['id'])
        recommendations = []
        
        for idx, (cluster, movie_id) in enumerate(zip(all_clusters, movies_df['id'])):
            if cluster == preferred_cluster and movie_id not in watched_ids:
                recommendations.append(idx)
        
        if not recommendations:
            return pd.DataFrame()
            
        return movies_df.iloc[recommendations[:n_recommendations]]
