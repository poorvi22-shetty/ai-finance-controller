import json
import os

from reconciliation import run_reconciliation


# ---------------- Load Ground Truth ----------------

def load_ground_truth():

    with open(
        "data/ground_truth.json",
        "r"
    ) as file:

        return json.load(file)


# ---------------- Create Ground Truth Map ----------------

def create_ground_truth_map(ground_truth):

    return {
        item["transaction_id"]:
            item["case_type"]

        for item in ground_truth
    }


# ---------------- Convert System Status ----------------

def convert_status_to_case_type(status):

    mapping = {

        "MATCH":
            "normal",

        "PRICING_MISMATCH":
            "pricing_mismatch",

        "SETTLEMENT_MISMATCH":
            "settlement_mismatch",

        "REFUND_ADJUSTMENT":
            "refund_adjustment",

        "REGIONAL_REVIEW":
            "ambiguous_location"
    }

    return mapping.get(
        status,
        "unresolved"
    )


# ---------------- Evaluate Predictions ----------------

def evaluate_predictions(
    results,
    ground_truth_map
):

    total = len(results)

    correct = 0

    predictions = []


    for result in results:

        transaction_id = (
            result["transaction_id"]
        )

        predicted = (
            convert_status_to_case_type(
                result["status"]
            )
        )

        actual = ground_truth_map.get(
            transaction_id,
            "unresolved"
        )

        is_correct = (
            predicted == actual
        )


        if is_correct:

            correct += 1


        predictions.append({

            "transaction_id":
                transaction_id,

            "predicted":
                predicted,

            "actual":
                actual,

            "correct":
                is_correct
        })


    accuracy = (

        correct / total * 100

        if total > 0

        else 0
    )


    return (
        predictions,
        round(accuracy, 2)
    )


# ---------------- Calculate Precision & Recall ----------------

def calculate_class_metrics(
    predictions,
    target_class
):

    true_positive = 0

    false_positive = 0

    false_negative = 0


    for item in predictions:

        predicted = item["predicted"]

        actual = item["actual"]


        if (
            predicted == target_class
            and actual == target_class
        ):

            true_positive += 1


        elif (
            predicted == target_class
            and actual != target_class
        ):

            false_positive += 1


        elif (
            predicted != target_class
            and actual == target_class
        ):

            false_negative += 1


    precision = (

        true_positive
        /
        (
            true_positive
            + false_positive
        )

        if (
            true_positive
            + false_positive
        ) > 0

        else 0
    )


    recall = (

        true_positive
        /
        (
            true_positive
            + false_negative
        )

        if (
            true_positive
            + false_negative
        ) > 0

        else 0
    )


    return {

        "precision":
            round(
                precision * 100,
                2
            ),

        "recall":
            round(
                recall * 100,
                2
            ),

        "true_positive":
            true_positive,

        "false_positive":
            false_positive,

        "false_negative":
            false_negative
    }


# ---------------- Build Evaluation Report ----------------

def build_evaluation_report(
    predictions,
    accuracy,
    processing_time
):

    classes = [

        "normal",

        "pricing_mismatch",

        "settlement_mismatch",

        "refund_adjustment",

        "ambiguous_location"
    ]


    class_metrics = {}


    for target_class in classes:

        class_metrics[target_class] = (
            calculate_class_metrics(
                predictions,
                target_class
            )
        )


    total = len(predictions)

    correct = sum(
        1
        for item in predictions
        if item["correct"]
    )

    incorrect = total - correct


    return {

        "total_records":
            total,

        "correct_predictions":
            correct,

        "incorrect_predictions":
            incorrect,

        "accuracy":
            accuracy,

        "processing_time_seconds":
            round(
                processing_time,
                6
            ),

        "class_metrics":
            class_metrics
    }


# ---------------- Save Evaluation Report ----------------

def save_evaluation_report(report):

    os.makedirs(
        "reports",
        exist_ok=True
    )


    report_path = (
        "reports/evaluation_report.json"
    )


    with open(
        report_path,
        "w"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )


    return report_path


# ---------------- Main ----------------

if __name__ == "__main__":

    results, processing_time = (
        run_reconciliation()
    )


    ground_truth = (
        load_ground_truth()
    )


    ground_truth_map = (
        create_ground_truth_map(
            ground_truth
        )
    )


    predictions, accuracy = (
        evaluate_predictions(
            results,
            ground_truth_map
        )
    )


    report = (
        build_evaluation_report(
            predictions,
            accuracy,
            processing_time
        )
    )


    report_path = (
        save_evaluation_report(
            report
        )
    )


    print(
        "\n========== "
        "MODEL EVALUATION "
        "==========\n"
    )


    print(
        f"Total records : "
        f"{report['total_records']}"
    )


    print(
        f"Correct predictions : "
        f"{report['correct_predictions']}"
    )


    print(
        f"Incorrect predictions : "
        f"{report['incorrect_predictions']}"
    )


    print(
        f"Accuracy : "
        f"{report['accuracy']}%"
    )


    print(
        f"Processing time : "
        f"{report['processing_time_seconds']:.4f} seconds"
    )


    print(
        "\n========== "
        "CLASS METRICS "
        "==========\n"
    )


    for target_class in report["class_metrics"]:

        metrics = (
            report["class_metrics"][
                target_class
            ]
        )


        print(
            f"\n{target_class.upper()}"
        )


        print(
            f"Precision: "
            f"{metrics['precision']}%"
        )


        print(
            f"Recall: "
            f"{metrics['recall']}%"
        )


        print(
            f"TP: "
            f"{metrics['true_positive']}"
        )


        print(
            f"FP: "
            f"{metrics['false_positive']}"
        )


        print(
            f"FN: "
            f"{metrics['false_negative']}"
        )


    print(
        "\nEvaluation report saved to:"
    )


    print(
        report_path
    )