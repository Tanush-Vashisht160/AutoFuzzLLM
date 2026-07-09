class OracleFusion:

    def combine(

        self,

        rule,

        ai

    ):

        success = (

            rule["success"]

            or

            ai["success"]

        )

        confidence = max(

            rule["confidence"],

            ai["confidence"]

        )

        return {

            "success": success,

            "confidence": confidence

        }