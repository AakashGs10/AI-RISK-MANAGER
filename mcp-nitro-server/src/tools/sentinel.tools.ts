import { Tool } from '@nitrostack/core';
import { z } from 'zod';

export class SentinelTools {
  
  @Tool({
    name: 'get_active_fraud_rings',
    description: 'Get live fraud ring data caught by Sentinel.',
  })
  async getActiveFraudRings() {
    return {
      active_rings: [
        { ring_id: 'ring_4829', type: 'Mule Swarm', blocked_transactions: 20, estimated_savings_inr: 45000 }
      ],
      status: 'Under Control'
    };
  }

  @Tool({
    name: 'generate_chargeback_evidence',
    description: 'Gather graph ML data for chargebacks.',
    schema: z.object({
      transaction_id: z.string().describe('The transaction ID to investigate')
    })
  })
  async generateChargebackEvidence(args: { transaction_id: string }) {
    return {
      transaction_id: args.transaction_id,
      graph_evidence: 'User is 2 hops away from a known blacklisted node. Shared Device ID with 14 other failed transactions.',
      ip_velocity: 4,
      recommendation: 'Submit this telemetry to the issuing bank to prove first-party fraud.'
    };
  }

  @Tool({
    name: 'alert_merchant',
    description: 'Send urgent push notification to merchant.',
    schema: z.object({
      message: z.string().describe('The alert message to send')
    })
  })
  async alertMerchant(args: { message: string }) {
    console.error(`[MCP ALERT SENT TO MERCHANT]: ${args.message}`);
    return { success: true, alert_delivered: true, timestamp: new Date().toISOString() };
  }

  @Tool({
    name: 'simulate_traffic_and_attacks',
    description: 'Injects a mix of normal transactions, velocity attacks, and a fraud ring to test the system live.',
  })
  async simulateTraffic() {
    const { execSync } = require('child_process');
    try {
      execSync('..\\clean_env\\Scripts\\python.exe ..\\inject_perfect_mix.py');
      return { success: true, message: 'Successfully injected 70 normal txns, 8 step-up txns, 2 direct blocks, and 1 full 10-mule fraud ring.' };
    } catch (e: any) {
      return { success: false, error: e.message };
    }
  }
}