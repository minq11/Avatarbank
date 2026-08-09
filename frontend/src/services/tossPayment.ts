/**
 * 토스페이먼츠 결제창 열기.
 *
 * SDK 는 index.html 에서 전역으로 로드한다 (window.TossPayments).
 * 서버가 확정한 주문(금액·주문번호)을 그대로 넘기는 게 핵심이다 —
 * 프론트에서 금액을 계산해 넘기면 위변조 여지가 생긴다.
 *
 * 결제 성공 시 토스가 successUrl 로 리다이렉트하고, 그 페이지에서 승인(confirm)이 일어난다.
 * 승인을 호출하지 않으면 결제는 자동 취소된다.
 */

import type { CreditOrder } from "./api";
import { creditsApi } from "./api";

declare global {
  interface Window {
    TossPayments?: (clientKey: string) => {
      payment: (options: { customerKey: string }) => {
        requestPayment: (options: Record<string, unknown>) => Promise<void>;
      };
    };
  }
}

/** 비회원 결제(customerKey 없이)로 처리한다는 뜻의 SDK 상수. */
const ANONYMOUS = "ANONYMOUS";

export async function openTossPayment(order: CreditOrder): Promise<void> {
  if (!window.TossPayments) {
    throw new Error("결제 모듈을 불러오지 못했어요. 새로고침 후 다시 시도해 주세요.");
  }
  if (!order.client_key) {
    throw new Error("결제가 아직 설정되지 않았어요.");
  }

  const toss = window.TossPayments(order.client_key);
  const payment = toss.payment({ customerKey: ANONYMOUS });

  try {
    await payment.requestPayment({
      method: "CARD",
      amount: { currency: "KRW", value: order.amount_krw },
      orderId: order.order_id,
      orderName: order.order_name,
      successUrl: order.success_url,
      failUrl: order.fail_url,
      card: {
        useEscrow: false,
        flowMode: "DEFAULT",
        useCardPoint: false,
        useAppCardOnly: false,
      },
    });
  } catch (e) {
    // 사용자가 결제창을 닫으면 여기로 온다. 대기 중인 주문을 정리해 두지 않으면
    // pending 주문이 계속 쌓인다. 정리 실패는 치명적이지 않으므로 삼킨다.
    void creditsApi.cancelOrder(order.order_id).catch(() => undefined);
    throw e;
  }
}
