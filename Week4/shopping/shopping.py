import calendar
import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4
K_NEIGHBORS = 1
POSITIVE = 1
NEGATIVE = 0
MONTH_COL = 10
VISITOR_TYPE_COL = 15
WEEKEND_COL = 16
REVENUE_COL = 17

def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        data.pop(0) # Removes the header row
    
    evidence = []
    labels = []

    for row in data:
        row[MONTH_COL] = convertMonthAbbrToNum(row[MONTH_COL]) # Converting month abbr to num
        row[VISITOR_TYPE_COL] = 1 if row[VISITOR_TYPE_COL] == "Returning_Visitor" else 0 # Converting to 0/1 representation of returning/not
        row[WEEKEND_COL] = 1 if row[WEEKEND_COL] == 'TRUE' else 0 # Convert string true and false to 0 and 1
        row[REVENUE_COL] = 1 if row[REVENUE_COL] == 'TRUE' else 0 # Convert string true and false to 0 and 1
        evidence.append(row[:-1])
        labels.append(row[-1])

    # I was trying to be too fancy...
    # evidence = [row[:-1] for row in data] # Evidence is every col but the last
    # evidence = [[convertMonthAbbrToNum(row[col]) if col == MONTH_COL else row[col]  # Convert month abbr to numbers
    #             for col in range(len(row))] for row in evidence]
    # labels = [row[-1] for row in data] # Labels are in the last col
    
    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=K_NEIGHBORS)
    return model.fit(evidence, labels)

def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    trueNeg = 0
    truePos = 0
    negTotal = 0
    posTotal = 0

    for actual, predicted in zip(labels, predictions):
        if actual == POSITIVE:
            posTotal += 1
            if actual == predicted:
                truePos += 1
        else:
            negTotal += 1    
            if actual == predicted:
                trueNeg += 1
    
    sensitivity = truePos / posTotal
    specificity = trueNeg / negTotal

    return (sensitivity, specificity)

def convertMonthAbbrToNum(monthAbbr):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "June", 
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] # Why is june the only 4 letters???

    for index in range(len(months)):
        if monthAbbr == months[index]:
            return index
 
if __name__ == "__main__":
    main()
