#!/usr/bin/env python

##############
#### Your name: Matthieu J. Capuano
##############

# References Used:
# http://scikit-image.org/docs/dev/auto_examples/features_detection/plot_hog.html?highlight=sift
# http://scikit-image.org/docs/dev/api/skimage.feature.html
# http://scikit-image.org/docs/dev/api/skimage.exposure.html#skimage.exposure.rescale_intensity

# Histogram Normalization (Made things worse): http://scikit-image.org/docs/dev/api/skimage.exposure.html#skimage.exposure.equalize_hist
# Gaussian Filtering (Made things worse): http://scikit-image.org/docs/dev/api/skimage.filters.html#skimage.filters.gaussian
# Prewitt Edge Detection instead of HOG (train accuracy: 100% test accuracy: 90%): http://scikit-image.org/docs/dev/api/skimage.filters.html#skimage.filters.prewitt

import numpy as np
import re
from sklearn import svm, metrics
from skimage import io, feature, filters, exposure, color

# MY IMPORTS:
from skimage.feature import hog

class ImageClassifier:
    
    def __init__(self):
        self.classifer = None

    def imread_convert(self, f):
        return io.imread(f).astype(np.uint8)

    def load_data_from_folder(self, dir):
        # read all images into an image collection
        ic = io.ImageCollection(dir+"*.bmp", load_func=self.imread_convert)
        
        #create one large array of image data
        data = io.concatenate_images(ic)
        
        #extract labels from image names
        labels = np.array(ic.files)
        for i, f in enumerate(labels):
            m = re.search("_", f)
            labels[i] = f[len(dir):m.start()]
        
        return(data,labels)

    def extract_image_features(self, data):
        # Please do not modify the header above

        # extract feature vector from image data

        ######################## YOUR CODE HERE ########################
        feature_data = np.zeros([data.shape[0], data.shape[1] * data.shape[2]])
        i = 0
        for image in data:
            # For the current image we run skimage.feature.hog; returns a HOG descriptor of the image, and a visualization of the HOG image.
            fd, hog_image = hog(image, orientations=32, pixels_per_cell=(64, 64), cells_per_block=(1, 1),
                                visualize=True, multichannel=True)

            # Stretches and shrinks intensity leves to given range.
            hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 10))

            # We reshape the 2D array for that image into a 1D array, that way we can train the SVM with a 2D array
            hog_image_rescaled_flat = np.reshape(hog_image_rescaled, (np.product(hog_image_rescaled.shape),))

            feature_data[i] = hog_image_rescaled_flat

            i = i + 1

        # Please do not modify the return type below
        return(feature_data)

    def train_classifier(self, train_data, train_labels):
        # Please do not modify the header above
        
        # train model and save the trained model to self.classifier
        
        ######################## YOUR CODE HERE ########################
        clf = svm.SVC(kernel='linear')
        clf.fit(train_data, train_labels)

        self.classifer = clf

    def predict_labels(self, data):
        # Please do not modify the header

        # predict labels of test data using trained model in self.classifier
        # the code below expects output to be stored in predicted_labels
        
        ########################
        ######## YOUR CODE HERE
        ########################
        clf = self.classifer
        predicted_labels = clf.predict(data)

        # Please do not modify the return type below
        return predicted_labels

      
def main():

    img_clf = ImageClassifier()

    # load images
    (train_raw, train_labels) = img_clf.load_data_from_folder('./train/')
    (test_raw, test_labels) = img_clf.load_data_from_folder('./test/')
    
    # convert images into features
    train_data = img_clf.extract_image_features(train_raw)
    test_data = img_clf.extract_image_features(test_raw)
    
    # train model and test on training data
    img_clf.train_classifier(train_data, train_labels)
    predicted_labels = img_clf.predict_labels(train_data)
    print("\nTraining results")
    print("=============================")
    print("Confusion Matrix:\n",metrics.confusion_matrix(train_labels, predicted_labels))
    print("Accuracy: ", metrics.accuracy_score(train_labels, predicted_labels))
    print("F1 score: ", metrics.f1_score(train_labels, predicted_labels, average='micro'))
    
    # test model
    predicted_labels = img_clf.predict_labels(test_data)
    print("\nTraining results")
    print("=============================")
    print("Confusion Matrix:\n",metrics.confusion_matrix(test_labels, predicted_labels))
    print("Accuracy: ", metrics.accuracy_score(test_labels, predicted_labels))
    print("F1 score: ", metrics.f1_score(test_labels, predicted_labels, average='micro'))


if __name__ == "__main__":
    main()
