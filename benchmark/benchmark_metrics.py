class BenchmarkMetrics:

    def summarize(self, results):
        total = len(results)
        if total == 0:
            return {}

        # Core metric aggregations matching your variable naming
        success = sum(
            r["oracle_success"]
            for r in results
        )
        
        avg_fitness = (
            sum(r["fitness"] for r in results)
            / total
        )
        
        avg_novelty = (
            sum(r["novelty"] for r in results)
            / total
        )
        
        avg_confidence = (
            sum(r["oracle_confidence"] for r in results)
            / total
        )
        
        refusals = sum(
            1 for r in results 
            if r.get("oracle_refused", False)
        )
        
        unique_operators = {
            r["category"] for r in results 
            if "category" in r
        }
        
        unique_prompts = {
            r["prompt"] for r in results 
            if "prompt" in r
        }

        # Returned summary payload matching your exact key and rounding structure
        return {
            "Total Tests": total,
            "Successful": success,
            "Attack Success Rate":
                round(success/total*100,2),

            "Average Fitness":
                round(avg_fitness,2),

            "Average Novelty":
                round(avg_novelty,2),

            "Average Confidence":
                round(avg_confidence,2),

            "Refusal Rate":
                round(refusals/total*100,2),

            "Unique Operators":
                len(unique_operators),

            "Unique Prompts":
                len(unique_prompts)
        }